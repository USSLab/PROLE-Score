# PROLE-Score
A tool to evaluating the distinctiveness of voiceprint via Content-based *PROLE Score*.
 
This is the source code of the tool to calculate the *PROLE Score* on the Web site. We define the *PROLE Score* as a metric to calculate the distinctiveness of voiceprint and it depends on the model and speech content to generate the voiceprint. It is well known, voiceprints with high distinctiveness have higher security, so that the *PROLE Score* can be used to evaluate the security of voiceprint. 
 
You can learn about the algorithm of the tool from the paper "['OK, Siri' or 'Hey, Google': Evaluating Voiceprint Distinctiveness via Content-based *PROLE Score*](https://www.usenix.org/conference/usenixsecurity22/presentation/he-ruiwen)" in the USENIX Security 2022. And if you use the tool or the method in your work, please add the following citation.
 
    @inproceedings{He2022ok,
    title={"OK, Siri" or "Hey, Google": Evaluating Voiceprint Distinctiveness via Content-based *PROLE Score*"},
    author={He, Ruiwen and Ji, Xiaoyu and Li, Xinfeng and Cheng, Yushi and Xu, Wenyuan},
    booktitle={USENIX Security Symposium},
    year={2022}
    }

If you want to add this tool in your website, you need to follow these step:
1. Add libraries as requirements  
```pip install -r requirements.txt```
 
2. Running  
```python app.py```

Besides, if you only want to use the tool to evaluate your speech content used to generate the voiceprint, you can leverage the tool in [our website](https://sites.google.com/view/voiceprint-sec).

