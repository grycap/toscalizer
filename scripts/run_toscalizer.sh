#!/bin/bash

# Check if TOSCA YAML file path is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <path/to/tosca/example.yml>"
    exit 1
fi

tosca_file="$1"

# Call the toscalizer
output=$(./toscalizer/toscalizer.py analyze "$tosca_file" -j)

# Check if output contains "tosca_type": "Kubernetes"
if grep -q '"tosca_type": "Kubernetes"' <<< "$output"; then
    echo "Detected Kubernetes TOSCA type."
    
    # Extract the image name
    image=$(echo "$output" | jq -r '.images[0]')

    echo "Scanning image $image"
    
    # Install Trivy
    sudo apt-get install -y wget apt-transport-https gnupg
    wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
    echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
    sudo apt-get update
    sudo snap install trivy
    
    # Run Trivy to analyze the image and save output
    trivy_output_file="$HOME/scan/trivy-output.json"
    trivy image "$image" -f json -o "$trivy_output_file"
    
    # Pass the output file to trivyHeaders.py
    python trivyHeaders.py "$trivy_output_file"
else
    echo "Detected OpenStack TOSCA type."
    
    # Extract port numbers separated by comma
    ports=$(echo "$output" | jq -r '[.ports.simple_node[].source] | unique | join(",")')
    echo "Opened ports: $ports"
    
    # Install IM-client
    pip install IM-client

    # Create the authfile.dat
    cat <<EOF > authfile.dat
    #InfrastructureManager auth
    type = InfrastructureManager; username = user; password = pass
    #Ramses
    id = one; type = OpenNebula; host = ramses.i3m.upv.es:2633; username = asanchez; password = RamsesOpenNebula9
EOF

    # Run im_client.py create and capture the output
    create_output=$(im_client.py -r https://im.egi.eu/im -a authfile.dat create "$tosca_file")
    echo "im_client.py create output: $create_output"

    # Extract the infrastructure ID from the output
    infra_id=$(echo "$create_output" | grep -oP 'Infrastructure successfully created with ID: \K[0-9a-f-]+')

    if [ -z "$infra_id" ]; then
        echo "Failed to create infrastructure."
        exit 1
    fi

    echo "Infrastructure ID: $infra_id"

    # Wait for the infrastructure to be ready
    im_client.py -r https://im.egi.eu/im -a authfile.dat wait "$infra_id"

    # Step 5: Run im_client.py getinfo
    getinfo_output=$(im_client.py -r https://im.egi.eu/im -a authfile.dat getinfo "$infra_id" net_interface.1.ip)
    echo "im_client.py getinfo output: $getinfo_output"

    # Extract the IP address from the output and save it
    ip_address=$(echo "$getinfo_output" | tail -n 1)
    echo "$ip_address" > $HOME/scan/doms.txt

    echo "IP Address: $ip_address"

    # Install and run Nikto
    git clone https://github.com/sullo/nikto.git
    perl nikto/program/nikto.pl -h $HOME/scan/doms.txt -p "$ports" -o $HOME/scan/nikto-report.txt

    # Connect to the infrastructure and run Pakiti-client
    im_client.py -r https://im.egi.eu/im -a authfile.dat sshvm "$infra_id" 0 << EOF
    git clone https://github.com/CESNET/pakiti-client.git
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y openssl perl libwww-perl liblwp-protocol-https-perl # sudo apt-get update && sudo apt-get upgrade -y && 
    cd pakiti-client
    pakiti-client/pakiti-client -o $HOME/scan/pakiti-report.txt --mode store-and-report # --url https://pakiti.egi.eu
EOF

fi
