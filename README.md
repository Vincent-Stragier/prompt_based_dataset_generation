# Prompt Based Datasets Generation for Assistive Tools

This project aims to generate datasets for various (mocked) assistive tools for visually impaired and blind individuals using a LLM (e.g., Llama 2).

## Requirements

- a Google account to access Google Drive and Google Colab
- a HuggingFace account to access the HuggingFace Model Hub
- a model running on Petals (see available Swarms [here](https://health.petals.dev/)). For this project, we used Stable Beluga 2.

## Usage

0. Generate a description of your tools as per `tools/tools.json` format.
1. Generate the desired prompts using `0_generate_prompts.ipynb`.
   1. This notebook make use of templates to generate numerous prompts, based on the tools description.
2. Generate the desired datasets with Petals on Colab using `1_generate_datasets.ipynb`.
   1. This notebook empowers the LLM to generate the dataset based on the prompts and the tools description.
3. Build your dataset(s) using `1_generate_datasets_with_petals_colab_CPU_only.ipynb`.
   1. This notebook will help to extract the generated `user requests` from the raw generation.
   2. It will also serve to do some basic analysis on the generated dataset and to build human evaluable extracts of the dataset.
