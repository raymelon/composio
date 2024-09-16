#! /bin/bash


export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export WORKSPACE_WAIT_TIMEOUT=300

instances_unresolved=(
	"django__django-11749"
)
instances_resolved=(
)

instances_left=()
for dir in ../test_xarray/*/; do
    dir=${dir%*/}  # remove trailing slash
    dir=${dir##*/}  # get only the directory name
    instances_left+=("$dir")
done




# Create a new array with elements from instances_left that are not in instances_resolved
instances=()
for instance in "${instances_left[@]}"; do
    if [[ ! " ${instances_resolved[*]} " =~ " ${instance} " ]]; then
        instances+=("$instance")
    fi
done

# instances=("${instances[@]:62}")
# Combine with instances_unresolved
instances=("${instances_unresolved[@]}" )

echo "Instances: ${instances[*]}"
echo "Number of instances: ${#instances[@]}"

instances_string=$(IFS=,; echo "${instances[*]}")

run_instance() {
    local instance=$1
    local run_id=$2
    LANGCHAIN_PROJECT=$instance python benchmark_copy.py --test-instance-ids $instance --run-id $run_id
}

# Set the number of instances to run in parallel
k=1
run_id="langgraph_agent_$(date +%s%N)"
echo "Run ID: $run_id"
# Run instances in parallel, k at a time
for ((i=0; i<${#instances[@]}; i+=k)); do
    # Get up to k instances
    docker rmi $(docker images -f "dangling=true" -q)
    batch=("${instances[@]:i:k}")
    
    # Run the batch in parallel
    for instance in "${batch[@]}"; do
        run_instance "$instance" "$run_id" &
    done
    
    # Wait for all background processes to finish before starting the next batch
    wait
    docker rmi $(docker images -f "dangling=true" -q)
done
