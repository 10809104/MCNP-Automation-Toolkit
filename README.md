# MCNP-Automation-Toolkit 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![C Language](https://img.shields.io/badge/language-C-green.svg)]()
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()

**A high‑performance workflow suite for MCNP6 simulations, bridging the gap between resource‑aware task orchestration and lightning‑fast data post‑processing.**

---

## 🌟 Why This Toolkit?

Running MCNP simulations often involves tedious manual work: babysitting system resources to avoid freezes, manually organizing piles of output files, and extracting tally data by hand. 

**MCNP-Automation-Toolkit** eliminates that drudgery with a dual‑engine approach:

- **The Orchestrator (Python)** – intelligently manages your hardware and schedules tasks so your PC stays responsive.
- **The Parser (C)** – extracts simulation results at blazing speed, turning messy `.o` files into clean spreadsheets.

Whether you’re running a single case or a hundred, this toolkit lets you focus on science, not housekeeping.

---

## 📦 Core Components

| Component | Language | What it does |
|-----------|----------|--------------|
| [**Runner / Orchestrator**](./Runner/README.md) | Python | Monitors CPU/RAM, queues input files, launches MCNP instances, and provides a retro‑style dashboard while you wait. |
| [**Data Parser**](./Parser/README.md) | C | Scans gigabytes of `.o` files, aligns tally results with your `source.csv`, and produces consolidated reports in CSV format. |

Both tools can be used independently, or you can chain them together for a fully automated workflow.

---

## 🚀 Quick Start

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/MCNP-Automation-Toolkit.git
cd MCNP-Automation-Toolkit
```

### 2️⃣ Build the C Parser (optional – pre‑built executables are also available)
```bash
cd Parser
gcc -o MCNP_Parser.exe main.c -lcomdlg32 -lshell32 -lgdi32 -lwininet -lurlmon -lshlwapi
```
> **Note**: You can skip this step by downloading `MCNP_Parser.exe` from the [Releases](https://github.com/10809104/MCNP-Automation-Toolkit/releases) page.

### 3️⃣ Install Python dependencies (if running from source)
```bash
cd ../Runner
pip install -r requirements.txt   # only requires psutil
```
> **Note**: You can skip this step by downloading `MCNP_Runner.exe` from the [Releases](https://github.com/10809104/MCNP-Automation-Toolkit/releases) page.

### 4️⃣ Run the full workflow
- **Option A (source)**: `python MCNP_Runner.py` or 
- **Option B (pre‑built)**: Download `MCNP_Runner.exe` from Releases and double‑click.

The GUI will guide you through selecting:
- Your MCNP environment batch file (e.g., `mcnp_630_env.bat`)
- The working directory containing your `model parameter`
- The specific `.i` input files to run
- CPU and RAM usage limits

After all simulations finish, you’ll be prompted to launch the **Data Parser** to generate reports.

---

## 📂 Project Structure

```
MCNP-Automation-Toolkit/
├── Runner/                     # Python source for the Orchestrator
│   ├── MCNP_Runner.py          # Main entry point
│   ├── requirements.txt        # Python dependencies
│   └── README.md               # Component‑specific docs
├── Parser/                      # C source for the Data Parser
│   ├── include/                 # Header files (config.h, tools.h)
│   ├── src/                     # main.c
│   ├── Scripts/                 # Helper scripts (e.g., merge.ps1 for Excel)
│   ├── other/                   # ico and other
│   └── README.md                # Component‑specific docs
├── Examples/                     # result image
└── README.md                      # This file
```

---

## 📜 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

> **Developer's Note**: This toolkit was born from real nuclear engineering research. You may encounter mixed Chinese/English comments in the source – a mark of its “battle‑tested” origins.

---

About ``` Parser/ ```You can get more from[MCNP-Data-Toolkit](https://github.com/10809104/MCNP-Data-Toolkit/)

**Now go automate your MCNP workflow!**  
*Made with ❤️ by KikKoh*
