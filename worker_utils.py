from MWSATInstance import MWSATInstance
import time
from simulated_annealing import simulated_annealing
import os
import concurrent.futures
import pandas as pd

def _worker_task(filepath, params, opt_val, n_repeats):
    """
    Worker function to run in a separate process.
    Loads the instance once and runs the algorithm n_repeats times.
    """
    results = []
    instance_name = os.path.basename(filepath)
    
    # Load instance once per process to save I/O
    try:
        instance = MWSATInstance(filepath)
        n_vars = instance.num_vars # Capture size for analysis
    except Exception as e:
        print(f"Error loading {instance_name}: {e}")
        return []

    for run_id in range(n_repeats):
        start_time = time.time()
        
        # Run Algorithm
        best_state, history = simulated_annealing(instance, **params)
        
        elapsed_time = time.time() - start_time
        
        # Calculate Metrics
        final_score = best_state.current_score
        is_valid = (best_state.clauses_satisfied == instance.num_clauses)
        
        
        success = is_valid and (final_score >= opt_val)
        rel_error = (opt_val - final_score) / opt_val if is_valid else 1.0 # 1.0 error if invalid
            # Cap error at 0 (if we somehow find better than known optimum)
        if rel_error < 0: rel_error = 0.0
    
            
        # Append Record
        results.append({
            "Instance": instance_name,
            "Is_Valid": is_valid,
            "Success": success,
            "Score": final_score,
            "Optimum": opt_val,
            "Rel_Error": rel_error,
            "Steps": len(history),
            "Time": elapsed_time
        })
        
    return results


def run_blackbox_parallel(instance_paths, solutions_dict, params, n_repeats=100, max_workers=None):
    all_records = []
    tasks = []
    
    print(f"--- Starting Black Box Evaluation ---")
    print(f"Instances: {len(instance_paths)}")
    print(f"Repeats per Instance: {n_repeats}")
    print(f"Total Runs: {len(instance_paths) * n_repeats}")
    print(f"Parallel Workers: {max_workers if max_workers else 'Auto'}")
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        
        for path in instance_paths:
            filename = os.path.basename(path)
            key = filename.split(".")[0]
            opt_val = solutions_dict.get(key, 0)
            
            future = executor.submit(_worker_task, path, params, opt_val, n_repeats)
            tasks.append(future)
        
        # Collect results
        for i, future in enumerate(concurrent.futures.as_completed(tasks)):
            try:
                data = future.result()
                all_records.extend(data)
                
                # Simple progress indicator
                if (i + 1) % 1 == 0: # Update every instance
                    print(f"Completed {i + 1}/{len(instance_paths)} instances...")
                    
            except Exception as e:
                print(f"Task generated an exception: {e}")

    print("--- Evaluation Complete ---")
    return pd.DataFrame(all_records)