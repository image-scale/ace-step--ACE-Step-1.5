@echo off
setlocal EnableDelayedExpansion

:: ACE-Step Gradio UI Launcher Script for Windows

:: Skip legacy torch compatibility fix if explicitly disabled
if /i "%ACESTEP_SKIP_LEGACY_TORCH_FIX%"=="true" (
    echo Skipping legacy NVIDIA torch compatibility check
    goto :StartApp
)

:: Run legacy NVIDIA compatibility check
call :EnsureLegacyNvidiaTorchCompat
if !ERRORLEVEL! NEQ 0 exit /b !ERRORLEVEL!

:StartApp
:: Start the Gradio UI
python -m acestep.ui.gradio %*
exit /b 0

:EnsureLegacyNvidiaTorchCompat
:: Probe Python compatibility for legacy NVIDIA GPUs
python -c "import torch; print(torch.cuda.is_available())" > nul 2>&1
set LEGACY_CHECK_EXIT=!ERRORLEVEL!

:: Check for legacy_torch_fix_probe_exit_code
if "!LEGACY_CHECK_EXIT!"=="0" (
    echo Compatibility check passed
    exit /b 0
) else (
    echo Warning: Compatibility probe failed
    echo Consider installing torch==2.5.1+cu121 for better compatibility
    exit /b !LEGACY_CHECK_EXIT!
)
