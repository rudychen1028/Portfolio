#!/bin/bash

# Function to restart Slurmctld on a node
restart_slurmctld() {
    local node=$1
    echo "Node: $node"
    ssh -XY -o StrictHostKeyChecking=no -i /asgc_ui_home/rudychen/.ssh/newops -l root $node systemctl restart slurmctld
    local success=$?
    if [ $success -eq 0 ]; then
        echo "Success!"
    else
        echo "Failed to restart slurmctld on $node"
    fi
}

# Function to reload Slurmd on a node
reload_slurmd() {
    local node=$1
    echo "Node: $node"
    timeout 60 ssh -XY -o StrictHostKeyChecking=no -i /asgc_ui_home/rudychen/.ssh/newops -l root $node systemctl reload slurmd
    local success=$?
    if [ $success -eq 0 ]; then
        echo "Success!"
    else
        echo "Failed to reload slurmd on $node"
    fi
}


#install pkg
install_pkg() {
    local node=$1
    echo "Node: $node"
    ssh -XY -o StrictHostKeyChecking=no -i /asgc_ui_home/rudychen/.ssh/newops -l root $node << 'EOF'
    sudo sed -i -e 's/^proxy=/#proxy=/' -e 's/^http_caching=/#http_caching=/' /etc/yum.conf
    yum install -y gsl && \
    yum install -y fftw2  fftw3 && \
    yum install -y hdf5-devel-1.8.12-13.el7.x86_64 \
    hdf-4.2.13-1.el7.x86_64 \
    hdf-devel-4.2.13-1.el7.x86_64 \
    hdf5-mpich-devel-1.8.12-13.el7.x86_64 \
    hdf5-mpich-static-1.8.12-13.el7.x86_64 \
    hdf5-mpich-1.8.12-13.el7.x86_64 \
    hdf5-static-1.8.12-13.el7.x86_64 \
    hdf5-1.8.12-13.el7.x86_64
EOF
    local success=$?
    if [ $success -eq 0 ]; then
        echo "Success!"
    else
        echo "Failed to install on $node"
    fi
}

# Restart Slurmctld on hpc-qdr4
restart_slurmctld "hpc-qdr4"

# Loop through the array of nodes and reload Slurmd
nodes=("slurm-ui01" "slurm-ui02" "slurm-ui03" "slurm-ui-asiop" "hp-teslav01" "hp-teslav02" "hp-teslav03" "hp-teslav04" "hp-teslaa01" "hp-teslaa03" "sma-wn01" "sma-wn02" "hpa-wn01" "hpa-wn02" "hpa-wn03" "hpa-wn04" "as-wn621" "as-wn622" "as-wn623" "as-wn624" "as-wn625" "as-wn626" "as-wn627" "as-wn628" "as-wn629" "as-wn630" "as-wn631" "as-wn632" "smwn001" "smwn002" "smwn003" "smwn004" "smwn005" "smwn006" "smwn007" "smwn008" "smwn009" "smwn010" "smwn011" "smwn012" "smwn013" "smwn014" "smwn015" "smwn016" "smwn017" "smwn018" "smwn019" "smwn020" "smwn021" "smwn022" "smwn023" "smwn024" "smwn025" "smwn026" "smwn027" "smwn028" "smwn029" "smwn030" "smwn031" "smwn032" "smwn033" "smwn034" "smwn035" "smwn036" "smwn037" "smwn038" "smwn039" "smwn040" "smwn041" "smwn042" "smwn043" "smwn044" "smwn045" "smwn046" "smwn047" "smwn048" "smwn049" "smwn050" "smwn051" "smwn052" "smwn053" "smwn054" "smwn055" "smwn056" "smwn057" "smwn058" "smwn059" "smwn060" "smwn061" "smwn062" "smwn063" "smwn064" "smwn065" "smwn066" "smwn067" "smwn068" "smwn069" "smwn070" "smwn071" "smwn072" "smwn073" "smwn074" "smwn075" "smwn076" "smwn077" "smwn078" "smwn079" "smwn080" "smwn081" "smwn082" "smwn083" "smwn084" "smwn085" "smwn086" "smwn087" "smwn088" "smwn089" "smwn090" "smwn091" "smwn092" "hpa-wn05" "hpa-wn06" "hpa-wn07" "hpa-wn08" "hpa-wn09" "hpa-wn10" "hpa-wn11" "hpa-wn12" "hpa-wn13" "hpa-wn14")

#nodes=("hp-teslav02" "hp-teslav03" "hp-teslav04" "hp-teslaa01" "hp-teslaa03" "sma-wn01" "sma-wn02" "hpa-wn01" "hpa-wn02" "hpa-wn03" "hpa-wn04" "as-wn621" "as-wn622" "as-wn623" "as-wn624" "as-wn625" "as-wn626" "as-wn627" "as-wn628" "as-wn629" "as-wn630" "as-wn631" "as-wn632" "smwn001" "smwn002" "smwn003" "smwn004" "smwn005" "smwn006" "smwn007" "smwn008" "smwn009" "smwn010" "smwn011" "smwn012" "smwn013" "smwn014" "smwn015" "smwn016" "smwn017" "smwn018" "smwn019" "smwn020" "smwn021" "smwn022" "smwn023" "smwn024" "smwn025" "smwn026" "smwn027" "smwn028" "smwn029" "smwn030" "smwn031" "smwn032" "smwn033" "smwn034" "smwn035" "smwn036" "smwn037" "smwn038" "smwn039" "smwn040" "smwn041" "smwn042" "smwn043" "smwn044" "smwn045" "smwn046" "smwn047" "smwn048" "smwn049" "smwn050" "smwn051" "smwn052" "smwn053" "smwn054" "smwn055" "smwn056" "smwn057" "smwn058" "smwn059" "smwn060" "smwn061" "smwn062" "smwn063" "smwn064" "smwn065" "smwn066" "smwn067" "smwn068" "smwn069" "smwn070" "smwn071" "smwn072" "smwn073" "smwn074" "smwn075" "smwn076" "smwn077" "smwn078" "smwn079" "smwn080" "smwn081" "smwn082" "smwn083" "smwn084" "smwn085" "smwn086" "smwn087" "smwn088" "smwn089" "smwn090" "smwn091" "smwn092" "hpa-wn05" "hpa-wn06" "hpa-wn07" "hpa-wn08" "hpa-wn09" "hpa-wn10" "hpa-wn11" "hpa-wn12" "hpa-wn13" "hpa-wn14")

#nodes=("hpa-wn05" "hpa-wn06" "hpa-wn07" "hpa-wn08" "hpa-wn09" "hpa-wn10" "hpa-wn11" "hpa-wn12" "hpa-wn13" "hpa-wn14")

for node in "${nodes[@]}"; do
    reload_slurmd "$node"
done
