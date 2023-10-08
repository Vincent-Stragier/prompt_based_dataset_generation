# -*- coding: utf-8 -*-
"""generate_dataset_with_petals

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YKPlifrMiizKnZXyUDR3obFEW5VPXk-y

<div align="center">
<img src="https://camo.githubusercontent.com/473dd9f992924d27457650251786464f72e54121ac6e9210add0f483ca849277/68747470733a2f2f692e696d6775722e636f6d2f3765523750616e2e706e67" width="40%">  
</div>

# Getting started with Petals

This notebook will guide you through the basics of Petals &mdash; a system for inference and fine-tuning large language models without the need to have high-end GPUs. With Petals, you can join compute resources with other people over the Internet and run large language models such as Llama 2 (70B), Stable Beluga 2, Llama-65B, Guanaco-65B, or BLOOM-176B right from your desktop computer or Google Colab.

💬 If you meet any issues while running this notebook, let us know in the **[#running-a-client](https://discord.gg/J29mCBNBvm)** channel of our Discord!

So, let's get started! First, let's install [the Petals package](https://github.com/bigscience-workshop/petals):
"""

# Commented out IPython magic to ensure Python compatibility.
# %pip install git+https://github.com/bigscience-workshop/petals

# !git clone https://github.com/Vincent-Stragier/prompt_based_dataset_generation

"""## Step 1. Loading the distributed model 🚀

Let's start with the easiest task &mdash; creating a distributed model and using it for generating text. This machine will download a small part of the model weights and rely on other computers in the network to run the rest of the model.

The Petals interface is compatible with PyTorch and the 🤗 [Transformers](https://github.com/huggingface/transformers) library &mdash; it feels like you're working with a local model even though its parts are hosted remotely. We suggest to start with [Stable Beluga 2 (70B)](https://huggingface.co/stabilityai/StableBeluga2), one of the best fine-tuned variants of Llama 2, but you can also use standard [Llama&nbsp;2&nbsp;(70B)](https://huggingface.co/meta-llama/Llama-2-70b-hf) if you have access to it (see below).
"""

# !huggingface-cli login


# model_name = "meta-llama/Llama-2-70b-chat-hf"
from tqdm import tqdm
import transformers
import os
import json
import torch
from transformers import AutoTokenizer
from petals import AutoDistributedModelForCausalLM
model_name = "petals-team/StableBeluga2"
# model_name = "tiiuae/falcon-180B-chat"
# You could also use "meta-llama/Llama-2-70b-chat-hf" or any other supported model from 🤗 Model Hub

tokenizer = AutoTokenizer.from_pretrained(
    model_name, use_fast=False, add_bos_token=False)
model = AutoDistributedModelForCausalLM.from_pretrained(model_name)
model = model.cuda()

"""🦙 **Want to run Llama 2?** Request access to its weights at the ♾️ [Meta AI website](https://ai.meta.com/resources/models-and-libraries/llama-downloads/) and 🤗 [Model Hub](https://huggingface.co/meta-llama/Llama-2-70b-hf) (make sure to use the same email),  get an 🔑 [access token](https://huggingface.co/settings/tokens), then run `!huggingface-cli login --token YOUR_TOKEN` before loading the model. Or just try it in our [chatbot app](https://chat.petals.dev).

📋 **Friendly reminder.** This Colab is provided for demo purposes. If you want to use these models in your own projects, make sure you follow their terms of use (see the ones for [Stable Beluga 2](https://huggingface.co/stabilityai/StableBeluga2/blob/main/LICENSE.txt) and [Llama 2](https://bit.ly/llama2-license)).

### ✍️ How to generate text?

Let's try to generate something by calling __`model.generate()`__ method.

The first call to this method takes a few seconds to connect to the Petals swarm. Once we do that, you should expect generation speed of up to **5-6 tokens/sec**. If you don't have enough GPU memory to host the entire model, this is much faster than what you get with other methods, such as offloading or running the model on CPU.
"""


def extract_prompts(path: str) -> list:
    with open(path, mode='r', encoding='utf-8') as json_file:
        return json.load(json_file)


print(os.listdir('prompt_based_dataset_generation/tools'))
prompts_0 = extract_prompts(
    'prompt_based_dataset_generation/tools/prompts_0.json')
prompts_1 = extract_prompts(
    'prompt_based_dataset_generation/tools/prompts_1.json')

# prompts_1[0]

# mount it
# from google.colab import drive
# drive.mount('/content/drive')

# DATA_DIR = f'/content/drive/MyDrive/thesis/2023/dataset_generation/{model_name}'
DATA_DIR = f'$HOME/thesis/2023/dataset_generation/{model_name}'
os.makedirs(DATA_DIR, mode=0o777, exist_ok=False)
# os.listdir(DATA_DIR)


def iterative_json_writer(element, json_file, last: bool = False):
    """Write an element of a JSON file.

    Args:
        element (any): The element to write.
        json_file (file): The file to write to.
        last (bool, optional): Whether this is the last element. Defaults to False.
    """
    # Add indentation
    json_file.write("    ")

    # Write element
    json.dump(element, json_file, indent=4)

    # Add comma if not last element
    if not last:
        json_file.write(",")

    # Add newline
    json_file.write("\n")


if model_name == "tiiuae/falcon-180B-chat":
    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device_map="auto",
    )


def generate_raw_dataset(input_data: list, output_file) -> None:
    prompts_outputs = []
    last_index = len(input_data) - 1

    with open(output_file, encoding='utf-8', mode='w') as json_file:
        json_file.write("[\n")

        for index, prompt in enumerate(tqdm(input_data)):
            inputs = tokenizer(prompt, return_tensors="pt")["input_ids"].cuda()
            # print(inputs)
            outputs = model.generate(inputs, max_new_tokens=2000)
            # prompts_outputs.append(tokenizer.decode(outputs[0]))
            iterative_json_writer(tokenizer.decode(
                outputs[0]), json_file, index == last_index)
            # print(tokenizer.decode(outputs[0]), '\n\n')
        json_file.write("]\n")

    # sequences = pipeline(
    #   "Girafatron is obsessed with giraffes, the most glorious animal on the face of this Earth. Giraftron believes all other animals are irrelevant when compared to the glorious majesty of the giraffe.\nDaniel: Hello, Girafatron!\nGirafatron:",
    #     max_length=200,
    #     do_sample=True,
    #     top_k=10,
    #     num_return_sequences=1,
    #     eos_token_id=tokenizer.eos_token_id,
    # )
    # for seq in sequences:
    #     print(f"Result: {seq['generated_text']}")


generate_raw_dataset(prompts_0, f'{DATA_DIR}/results_prompts_0.json')
generate_raw_dataset(prompts_1, f'{DATA_DIR}/results_prompts_1.json')

"""The `model.generate()` method runs **greedy** generation by default, but you can use many other generation methods like **top-p/top-k sampling** or **beam search** &mdash; just set proper arguments for the 🤗 Transformers [.generate()](https://huggingface.co/blog/how-to-generate) method.

🔏 **Note:** Your data is processed by other people in the public swarm. Learn more about privacy [here](https://github.com/bigscience-workshop/petals/wiki/Security,-privacy,-and-AI-safety). For sensitive data, you can set up a [private swarm](https://github.com/bigscience-workshop/petals/wiki/Launch-your-own-swarm) among people you trust.

## Step 2. Generating tokens on the fly and making chatbots 🕊️

If you'd like to talk to the model in an interactive way, you can use the __inference session__ interface &mdash; it allows to print generated tokens on the fly or make a chat bot that responds to human's inputs.

The inference session looks for a sequence of servers to run successive inference steps and store past attention caches. This way, you don't need to rerun previous tokens through the transformer to generate each phrase. If one of the servers disconnects or fails, Petals will automatically find a replacement and regenerate only a small part of the caches.

We provide a scheme of what's going on below, and you can check out servers that are actually online right now in our 🏥 [health monitor](https://health.petals.dev):

<br>
<div align="center">
<img src="https://i.imgur.com/fKR9BSP.png" width="70%">
</div>

Let's see how to show tokens on the fly, as soon as they are generated:
"""

# fake_token = tokenizer("^")["input_ids"][0]  # Workaround to make tokenizer.decode() keep leading spaces

# text = "What is a good chatbot? Answer:"
# prefix = tokenizer(text, return_tensors="pt")["input_ids"].cuda()

# with model.inference_session(max_length=30) as sess:
#     for i in range(20):
#         # Prefix is passed only for the 1st token of the outputs
#         inputs = prefix if i == 0 else None

#         # Let's use sampling with temperature = 0.9 and top_p = 0.6 to get more diverse results
#         outputs = model.generate(inputs, max_new_tokens=1, session=sess,
#                                  do_sample=True, temperature=0.9, top_p=0.6)

#         text += tokenizer.decode([fake_token, outputs[0, -1].item()])[1:]
#         print(text)

# """### Writing a simple chatbot 💬

# Now, let's proceed to writing a simple chatbot! We'll need one more loop that accepts inputs from a human, then runs generation until we get a newline (**`\n`**):
# """

# with model.inference_session(max_length=512) as sess:
#     while True:
#         prompt = input('Human: ')
#         if prompt == "":
#             break
#         prefix = f"Human: {prompt}\nFriendly AI:"
#         prefix = tokenizer(prefix, return_tensors="pt")["input_ids"].cuda()
#         print("Friendly AI:", end="", flush=True)

#         while True:
#             outputs = model.generate(prefix, max_new_tokens=1, session=sess,
#                                      do_sample=True, temperature=0.9, top_p=0.6)
#             outputs = tokenizer.decode([fake_token, outputs[0, -1].item()])[1:]

#             # Now, let's print one new token at a time
#             print(outputs, end="", flush=True)

#             if "\n" in outputs or "</s>" in outputs:
#                 break
#             prefix = None  # Prefix is passed only for the 1st token of the bot's response

# """📦 **Deploying apps that use Petals.** You can wrap up your code into a web app available for other people. As an example, take a look at our 💬&nbsp;[chatbot web app](https://chat.petals.dev) that uses this 🗼 [HTTP endpoint](https://github.com/petals-infra/chat.petals.dev#apis) for inference under the hood.

# ## Step 3. How does it work? 🛠️

# The `model` you are running is equal to the original model, but only a part of it is loaded into your machine's GPU. Let's have a look under the hood:
# """

# model

# """As you can see, word embeddings and some other layers are regular PyTorch modules hosted on your machine, but the rest of the model (e.g., transformers blocks) is encased in the __`RemoteSequential`__ class. This is an advanced PyTorch module that runs on a distributed swarm of other machines.

# Still, you can access individual layers and their outputs, as well as run forward/backward through them:
# """

# first_five_layers = model.model.layers[0:5]
# first_five_layers

# dummy_inputs = torch.randn(1, 3, model.config.hidden_size, dtype=torch.bfloat16, requires_grad=True)
# outputs = first_five_layers(dummy_inputs)
# outputs

# loss = torch.mean((outputs - torch.ones_like(outputs)) ** 2)
# loss.backward()  # backpropagate through the internet
# print("Grad w.r.t. inputs:", dummy_inputs.grad.flatten())

# """You can see that PyTorch can calculate gradients through remote blocks, which we'll later use to run fine-tuning!

# Note that, in general, you can mix and match distributed layers like in regular PyTorch and even insert and train your own layers (e.g., adapters) between the pre-trained ones. You can find further technical details in our [research paper](https://arxiv.org/pdf/2209.01188.pdf).

# ## Step 4. Prompt-tuning, or making a fox innocent 🦊

# While the remotely hosted transformer blocks are frozen to keep the pretrained model the same for all users, using **parameter-efficient fine-tuning** methods like trainable prompts or adapters (e.g., [LoRA](https://arxiv.org/abs/2106.09685)) is usually enough to make the model solve most downstream tasks. This way, all trainable parameters and the optimizer will be hosted locally, so you'd be able to fine-tune the model without interfering with other users.

# In this section, we'll use **trainable prompts** to solve a dummy task &mdash; take the model saying "*A quick brown fox jumps over the lazy dog.*" and teach it to say the opposite &ndash; that actually "*A quick brown fox did not jump over the lazy dog*".

# Let's see how the off-the-shelf model behaves on this task:
# """

# inputs = tokenizer("A quick brown fox", return_tensors="pt")["input_ids"].cuda()
# outputs = model.generate(inputs, max_new_tokens=7)
# print("generated:", tokenizer.decode(outputs[0]))

# """If you aren't familiar with prompt tuning, **trainable prompts** are just a few trainable "tokens" added before the inputs of your model. **Deep prompt tuning** adds extra trainable "tokens" for each transformer block &mdash; this way we'll have more trainable parameters:

# <div align="center">
# <img src="https://i.imgur.com/eohYuNE.png" width="60%">
# </div>

# **Figure.** The scheme of **deep prompt tuning** from Liu, Xiao, et al. ["P-tuning v2: Prompt tuning can be comparable to fine-tuning universally across scales and tasks."](https://arxiv.org/abs/2110.07602).

# Petals supports prompt tuning (**`tuning_mode="ptune"`**) and deep prompt tuning (**`tuning_mode="deep_ptune"`**) out of the box. Let's use deep prompt tuning with 3 tokens for input and each transformer block (**`pre_seq_len=3`**):
# """

# model = AutoDistributedModelForCausalLM.from_pretrained(model_name, tuning_mode='deep_ptune', pre_seq_len=3)
# model = model.cuda()

# """Now, we can create an Adam optimizer and fine-tune the distributed model &mdash; all done in the same way as if you were training a local model:"""

# opt = torch.optim.Adam(model.parameters(), lr=1e-3)

# the_fox_is_innocent = tokenizer("A quick brown fox did not jump over the lazy dog", return_tensors="pt")["input_ids"].cuda()
# for i in range(12):
#     loss = model(input_ids=the_fox_is_innocent, labels=the_fox_is_innocent).loss
#     print(f"loss[{i}] = {loss.item():.3f}")

#     opt.zero_grad()
#     loss.backward()
#     opt.step()
#     print("opt.step()")

# """Once the loss function is close to zero, you can see that the model continues the sentence as we want it to:"""

# inputs = tokenizer("A quick brown fox", return_tensors="pt")["input_ids"].cuda()
# outputs = model.generate(inputs, max_new_tokens=7)
# print("generated:", tokenizer.decode(outputs[0]))

# """## Step 5. Fine-tuning a trainable adapter 🏋️

# In this section, we'll try another popular fine-tuning method &mdash; adding **trainable adapters** to the model. These are small trainable layers added between the pretrained transformer blocks or in addition to some block weights.

# Here, we'll add a basic **trainable** linear layer in the middle of the pretrained model and swap the model's head to perform a **classification task**
# instead of generating text. As earlier, this layer's weights and the corresponding optimizer statistics will be stored locally:
# """

# import torch.nn as nn
# import torch.nn.functional as F

# model = AutoDistributedModelForCausalLM.from_pretrained(model_name)
# model = model.cuda()

# class LLMBasedClassifier(nn.Module):
#   def __init__(self, model):
#     super().__init__()
#     self.distributed_layers = model.transformer.h
#     self.adapter = nn.Sequential(nn.Linear(model.config.hidden_size, 32), nn.Linear(32, model.config.hidden_size))
#     self.head = nn.Linear(model.config.hidden_size, 2)

#   def forward(self, embeddings):
#     mid_block = len(self.distributed_layers) // 2
#     hidden_states = self.distributed_layers[:mid_block](embeddings)
#     hidden_states = self.adapter(hidden_states)
#     hidden_states = self.distributed_layers[mid_block:](hidden_states)
#     pooled_states = torch.mean(hidden_states, dim=1)
#     return self.head(pooled_states)

# """Now, let's take the Adam optimizer and train the model with a cross-entropy loss, which is typically used for classification:"""

# classifier = LLMBasedClassifier(model).cuda()
# opt = torch.optim.Adam(classifier.parameters(), 3e-5)
# inputs = torch.randn(3, 2, model.config.hidden_size, device='cuda')
# labels = torch.tensor([1, 0, 1], device='cuda')

# for i in range(5):
#   loss = F.cross_entropy(classifier(inputs), labels)
#   print(f"loss[{i}] = {loss.item():.3f}")
#   opt.zero_grad()
#   loss.backward()
#   opt.step()

# print('predicted:', classifier(inputs).argmax(-1))  # l, o, l

# """You can see that the loss is decreasing &mdash; that is, the model overfits to our dummy dataset! If you're further interested in a full-fledged example of fine-tuning on a classification task, check out [this notebook](https://colab.research.google.com/github/bigscience-workshop/petals/blob/main/examples/prompt-tuning-sst2.ipynb) where we fine-tune Llama on the popular SST2 dataset.

# ## Step 6. Using custom sampling methods 🎰

# In **Step 3**, you've seen that you can write normal PyTorch code to work with the parts of our distributed model. In practice, you can use it to implement many tricky fine-tuning and sampling methods &mdash; something you can't usually do with hosted APIs.

# Let's show how to implement your own **sampling method** from scratch. The __`model.inference_session()`__ interface in Petals allows you to write custom inference code. You can use this to implement any sampling algorithms you want, as well as write a custom beam search algorithm (e.g., to forbid the model from using swearwords).

# Below, we reimplement the standard `model.generate()` interface by making forward passes through all the layers manually:
# """

# from hivemind import get_logger

# logger = get_logger()

# fake_token = tokenizer("^")["input_ids"][0]  # Workaround to make tokenizer.decode() keep leading spaces

# text = "What is a good chatbot? Answer:"
# token_ids = tokenizer(text, return_tensors="pt")["input_ids"].cuda()
# max_length = 100
# with torch.inference_mode():
#     with model.inference_session(max_length=max_length) as sess:
#         while len(text) < max_length:
#             embs = model.transformer.word_embeddings(token_ids)
#             embs = model.transformer.word_embeddings_layernorm(embs)

#             h = sess.step(embs)
#             h_last = model.transformer.ln_f(h[:, -1])
#             logits = model.lm_head(h_last)

#             next_token = logits.argmax(dim=-1)
#             text += tokenizer.decode([fake_token, next_token.item()])[1:]
#             token_ids = next_token.reshape(1, 1)
#             logger.info(text)

# """## Step 7. Sharing is caring 🤗

# Petals is a community-run system &mdash; we rely on people sharing their GPUs. You can check out available servers on our [swarm monitor](https://health.petals.dev) and connect your GPU to help serving one of the models!

# 🐍 **Linux + Anaconda.** Run these commands:

# ```bash
# conda install pytorch pytorch-cuda=11.7 -c pytorch -c nvidia
# pip install git+https://github.com/bigscience-workshop/petals
# python -m petals.cli.run_server petals-team/StableBeluga2
# ```

# 🪟 **Windows + WSL.** Follow the guide on our [Wiki](https://github.com/bigscience-workshop/petals/wiki/Run-Petals-server-on-Windows).

# 🐋 **Any OS + Docker.** Run our [Docker](https://www.docker.com) image:

# ```bash
# sudo docker run -p 31330:31330 --ipc host --gpus all --volume petals-cache:/cache --rm learningathome/petals:main \
#     python -m petals.cli.run_server --port 31330 petals-team/StableBeluga2
# ```

# These commands will host a part of [Stable Beluga 2](https://huggingface.co/stabilityai/StableBeluga2) on your machine. You can also host `meta-llama/Llama-2-70b-hf`, `meta-llama/Llama-2-70b-chat-hf`, repos with Llama-65B, `bigscience/bloom`, `bigscience/bloomz`, and other compatible models from 🤗 [Model Hub](https://huggingface.co/models), or [add support](https://github.com/bigscience-workshop/petals/wiki/Run-a-custom-model-with-Petals) for new model architectures.

# 🦙 **Want to host Llama 2?** Request access to its weights at the ♾️ [Meta AI website](https://ai.meta.com/resources/models-and-libraries/llama-downloads/) and 🤗 [Model Hub](https://huggingface.co/meta-llama/Llama-2-70b-hf), generate an 🔑 [access token](https://huggingface.co/settings/tokens), then use this command for `petals.cli.run_server`:

# ```bash
# python -m petals.cli.run_server meta-llama/Llama-2-70b-chat-hf --token YOUR_TOKEN_HERE
# ```

# 💬 **FAQ.** Check out our [Wiki](https://github.com/bigscience-workshop/petals/wiki/FAQ:-Frequently-asked-questions#running-a-server) to learn how to use multple GPUs, restart the server on reboot, etc. If you have any issues, ping us in [our Discord](https://discord.gg/D9MwApKgWa)!

# 🔒 **Security.** Hosting a server does not allow others to run custom code on your computer. Learn more [here](https://github.com/bigscience-workshop/petals/wiki/Security,-privacy,-and-AI-safety).

# 🏆 **Thank you!** Once you load and host 10+ blocks, we can show your name or link on the [swarm monitor](https://health.petals.dev) as a way to say thanks. You can specify them with `--public_name YOUR_NAME`.

# ## What's next?

# Congratulations on finishing our tutorial! You've learned how to use Petals for different tasks, how it works under the hood, and how to increase its capacity.

# You can find a few other helpful resources below:

# * __More about Petals.__ The [README](https://github.com/bigscience-workshop/petals#readme) file in our GitHub repository has links to more Petals-related materials, including instructions for starting a private swarm and adding new models.

# * __Discord server.__ If you have any feedback, questions, or technical issues, please [join our Discord server](https://discord.gg/D9MwApKgWa) and let us know. If you want to build something based on Petals, we'd be happy to hear what you are up to.

# * __Research paper.__ Our [paper](https://arxiv.org/abs/2209.01188) shares more details about our research and what happens in Petals under the hood.
# """
