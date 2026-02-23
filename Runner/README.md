# MCNP Runner & Orchestrator (Python) 📟

**The intelligent "Command Center" for your MCNP6 simulations. Automating task scheduling, environment setup, and hardware resource optimization.**

---

## ✨ Features

* **Hardware-Aware Scheduling**: Dynamically monitors CPU and RAM usage via `psutil`. It intelligently queues tasks and only launches new simulations when system resources are below your specified safety thresholds.
* **Streamlined Workspace**:
* Automatically handles file I/O: copies `.i` files to the workspace.
* Post-simulation cleanup: moves `.o` files back to their original directories.


* **Environment Integration**: Seamlessly calls official `.bat` environment files to ensure MCNP6 executes with the correct internal paths and licenses.
* **The Retro Mode (Idle Experience)**: When the system is waiting for resources, the terminal transforms into a nostalgic 80s DOS-style interface.

---

## 🚀 How to Run

### Option A: Standalone Executable (Recommended)

Download `MCNP_Runner.exe` from the [Releases](https://github.com/10809104/MCNP-Automation-Toolkit/releases) page.

1. Double-click to launch.
2. Follow the GUI prompts to:
* Select your **MCNP Environment Batch File** (e.g., `mcnp_630_env.bat`).
* Choose your **Model Directory** and the specific `.i` files to run.
* Set your **CPU & RAM usage limits** (percentage).


3. Sit back and watch the simulation progress.

### Option B: Run from Source

If you want to run the script directly:

1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
```bash
pip install psutil

```


3. Execute the script:
```bash
python MCNP_Runner.py

```

---

## 📂 Code Structure

```

Main Thread
 ├── Manager Thread
 │     ├── Worker Threads
 │     └── display_status (run/stop)
 │
 ├── ResourceMonitor Thread
 │
 └── RetroRunner Thread

```

---


## 🕹️ Retro Terminal Mode

One of the unique aspects of this runner is its **interactive idle mode**. If the orchestrator stays idle for more than 20 seconds, it triggers a retro-themed environment:

* **Simulated BIOS**: Watch a nostalgic boot sequence.
* **Internal Commands**:
* `STATUS`: Get real-time updates on active MCNP tasks.
* `DIR`: Browse the "virtual" file system.
* `GAME`: Launch a built-in retro mini-game (`SHOT 'EM UP`) to kill time while waiting for long simulations to finish.
* `EXIT`: Return to the standard real-time monitor.



---

## 🛠 Project Integration

This runner is designed to work in tandem with the [C-based Data Parser](./Parser/README.md).

Upon completion of all simulation tasks, the Runner will automatically prompt you to initiate the **Report Generation** phase. This ensures a seamless transition from "Running Physics" to "Analyzing Data."

---

## 📋 Requirements

* **OS**: Windows 7/10/11 (Uses Windows-specific APIs for UI and process calling).
* **MCNP**: Must have a valid MCNP6 installation and a configured environment batch file.

---

## 📜 License

Licensed under the **MIT License**.

> **Developer's Note**: The Python orchestrator is built for resilience. It includes robust error handling to ensure that even if one MCNP task fails, the entire batch continues to process. Some comments in the code remain in Chinese to preserve the original development context from nuclear research labs.

---