# Data preparation scripts 

## Table of Contents
- [Downloading Data](#downloading-data)
- [Preparing the Data](#preparing-the-data)
- [Cite us](#how-to-cite-us)

---
## Downloading Data

For the experiments carried out in this paper, you need to download the data folder one by one as follows:

### ATCO2 test set corpus

- Download (purchase) the full test set (used in the paper): http://catalog.elra.info/en-us/repository/browse/ELRA-S0484/
- Download a free sample of the test set (only contains 1 hour of data): https://www.atco2.org/data 

**Dataset is in HuggingFace**:https://huggingface.co/datasets/Jzuluaga/atco2 |  <a href="https://huggingface.co/datasets/Jzuluaga/atco2"><img alt="GitHub" src="https://img.shields.io/badge/%F0%9F%A4%97-Dataset%20on%20Hub-yellow"> </a>

### UWB-ATCC corpus

The Air Traffic Control Communication corpus, or UWB-ATCC corpus, contains recordings of communication between air traffic controllers and pilots. The speech is manually transcribed and labeled with the information about the speaker (pilot/controller, not the full identity of the person). The audio data format is: 8kHz, 16bit PCM, mono.

You can download for free in: https://lindat.mff.cuni.cz/repository/xmlui/handle/11858/00-097C-0000-0001-CCA1-0

This item is Publicly Available and licensed under: Creative Commons - Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) 

**Dataset is in HuggingFace:** https://huggingface.co/datasets/Jzuluaga/uwb_atcc | <a href="https://huggingface.co/datasets/Jzuluaga/uwb_atcc"><img alt="GitHub" src="https://img.shields.io/badge/%F0%9F%A4%97-Dataset%20on%20Hub-yellow"> </a>

### LDC-ATCC corpus

The Air Traffic Control Complete (LDC94S14A) or LDC-ATCC corpus comprises recorded speech for use in supporting research and development activities in the area of robust speech recognition in domains similar to air traffic control (several speakers, noisy channels, relatively small vocabulary, constrained languaged, etc.) The audio data is composed of voice communication traffic between various controllers and pilots. The audio files are 8 KHz, 16-bit linear sampled data, representing continuous monitoring, without squelch or silence elimination, of a single FAA frequency for one to two hours.

You can purchase it and download here: https://catalog.ldc.upenn.edu/LDC94S14A


---
## Preparing the Data

The folder containing the preparation scripts to format and prepare each dataset looks like:

```
data/databases/
├── atco2_corpus
│   ├── data_prepare_atco2_corpus.sh
│   └── exp_prepare_atco2_corpus.sh
├── ldc_atcc
│   ├── data_prepare_ldc_atcc_corpus.sh
│   ├── exp_prepare_ldc_atcc_corpus.sh
│   ├── link_acronyms.sh
│   └── parse_lisp_array.sh
└── uwb_atcc
    ├── data_prepare_uwb_atcc_corpus.sh
    ├── exp_prepare_uwb_atcc_corpus.sh
    └── spk_id_tagger.py
```

You can format only one database and do all the experiments with it! **For instance**, [UWB-ATCC corpus](https://lindat.mff.cuni.cz/repository/xmlui/handle/11858/00-097C-0000-0001-CCA1-0) is completly free to download and use! You can start right away with it!

### Prepare only one database: UWB-ATCC use case

For preparing one database, you can simply go to root directory and run:

```bash 
conda activate diarization
bash data/databases/data_prepare_uwb_atcc.sh
bash data/databases/exp_prepare_uwb_atcc.sh
```

That will generate the files required for all the experiments in `experiments/data/uwb_atcc`. 


### Prepare all 3 databases

Don't worry! We have prepared a bash script/wrapper to format and prepare the 3 databases simultaneously. Go to the project root directory (one level up) and run:

```bash 
conda activate diarization
bash data/PREPARE_AND_FORMAT_DATASETS.sh
```

This will prepare each dataset in KALDI format (**you DO NOT need to install KALDI**). The outputs are generated in the `experiments/data/*` folder (around 203 MB of space for the 3 databases), and its structure should be:

```
experiments/data/
├── atco2_corpus
│   ├── prep
│   └── test
│       ├── diarization
│       └── diarization_acoustic
│           └── wav_path
├── ldc_atcc
│   ├── prep
│   ├── test
│   │   ├── diarization
│   │   └── diarization_acoustic
│   │       └── wav_path
│   └── train
│       ├── diarization
│       └── diarization_augmented
└── uwb_atcc
    ├── prep
    ├── test
    │   ├── diarization
    │   └── diarization_acoustic
    │       ├── prep
    │       └── wav_path
    └── train
        ├── diarization
        └── diarization_augmented
```

Where `atco2_corpus`, `ldc_atcc`, and `uwb_atcc` are the 3 **public datasets** used in the [BERT-based diarization paper](https://arxiv.org/abs/2110.05781).

Each folder contains a `diarization` folder. The diarization folder contains the file required (`utt2text_tags`) for training the BERT model in NER style.

```
!!! LDC-ATC and UWB-ATCC are used for training and testing, while ATCO2-test-set corpus only for testing. 
```

### Description of folder naming 

You can see in the `tree` above that there are 3 diarization folders:

- **diarization**: default folder to perform text-based diarization with a BERT module
- **diarization_augmented**: folder to perform text-based diarization with a BERT module, but using DATA AUGMENTATION. See the script in [data_augmentation_diarization.py](utils/augmentation/data_augmentation_diarization.py)
- **diarization_acoustic**: folder to perform acoustic-based diarization with [VBx system](https://github.com/BUTSpeechFIT/VBx) module. In this case, we created a script to merge segments from the original test sets. See the script in [generate_mixed_rttm_kaldi.py](utils/augmentation/generate_mixed_rttm_kaldi.py)

---
# How to cite us

If you use this code for your research, please cite our paper with:

Zuluaga-Gomez, J., Sarfjoo, S. S., Prasad, A., Nigmatulina, I., Motlicek, P., Ondrej, K., Ohneiser, O., & Helmke, H. (2021). BERTraffic: BERT-based Joint Speaker Role and Speaker Change Detection for Air Traffic Control Communications. 2022 IEEE Spoken Language Technology Workshop (SLT), Doha, Qatar.

Or use the bibtex item:

```
@article{zuluaga2022bertraffic,
  title={BERTraffic: BERT-based Joint Speaker Role and Speaker Change Detection for Air Traffic Control Communications},
  author={Zuluaga-Gomez, Juan and Sarfjoo, Seyyed Saeed and Prasad, Amrutha and Nigmatulina, Iuliia and Motlicek, Petr and Ondre, Karel and Ohneiser, Oliver and Helmke, Hartmut},
  journal={IEEE Spoken Language Technology Workshop (SLT), Doha, Qatar},
  year={2022}
  }
```


