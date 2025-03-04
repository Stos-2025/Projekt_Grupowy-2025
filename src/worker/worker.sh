#!/bin/ash

init(){
    rm -Rf /data/*

    mkdir /data/bin
    mkdir /data/out
    mkdir /data/src
    mkdir /data/std
    mkdir -p /data/tests/in
    mkdir /data/tests/out
    chmod -R 777 /data 

    rm -f /tmp/out/*
    rm -f /tmp/std/*
    rm -f /tmp/bin/*

    cp -R /tmp/* /data
    
    chmod -R 777 /data 

    ls -l /data
}

end(){
    cp -R /data/out/* /tmp/out
}

run(){

    echo "compilation"

    docker run \
        --rm \
        --cpus=1.0 \
        --ulimit cpu=30:30 \
        --network none \
        --security-opt no-new-privileges \
        -e SRC=/data/src \
        -e OUT=/data/out \
        -e BIN=/data/bin \
        -v conf_worker_data:/data:rw \
        comp

    if ! [ $? -eq 0 ]; then
        return
    fi

    echo "execution"

    docker run \
        --rm \
        --ulimit cpu=30:30 \
        --network none \
        --security-opt no-new-privileges \
        -e IN=/data/tests/in \
        -e OUT=/data/out \
        -e STD=/data/std \
        -e BIN=/data/bin \
        -e LOGS=on \
        -v conf_worker_data:/data:rw \
        exec

    if ! [ $? -eq 0 ]; then
        return
    fi

    echo "judging"

    docker run \
        --rm \
        --ulimit cpu=30:30 \
        --network none \
        --security-opt no-new-privileges \
        -e IN=/data/std \
        -e OUT=/data/out \
        -e ANS=/data/tests/out \
        -e LOGS=on \
        -v conf_worker_data:/data:rw \
        judge

    if ! [ $? -eq 0 ]; then
        return
    fi
}

echo "init"
init
echo "run"
run
echo "end"
end