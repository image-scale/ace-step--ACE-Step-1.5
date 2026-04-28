#!/bin/bash
# ACE-Step Gradio UI Launcher Script

set -e

# Skip legacy torch compatibility fix if explicitly disabled
if [ "$ACESTEP_SKIP_LEGACY_TORCH_FIX" = "true" ]; then
    echo "Skipping legacy NVIDIA torch compatibility check (ACESTEP_SKIP_LEGACY_TORCH_FIX=true)"
else
    # Run legacy NVIDIA compatibility probe
    legacy_torch_fix_probe_exit_code() {
        python -c "import torch; print(torch.cuda.is_available())" > /dev/null 2>&1
        return $?
    }

    legacy_torch_fix_probe_exit_code
    compat_status=$?

    if [ $compat_status -ne 0 ]; then
        echo "Warning: legacy NVIDIA compatibility probe failed with exit code $compat_status"
        echo "Consider installing torch==2.5.1+cu121 for better compatibility"
        return 1
    fi
fi

# Start the Gradio UI
python -m acestep.ui.gradio "$@"
