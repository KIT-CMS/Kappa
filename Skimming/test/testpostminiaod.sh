# year 2016
for dtype in data embedding MC;
    do cmsRun Kappa/Skimming/python/postMiniAODSequences.py year=2016 dtype=${dtype}
done;

# year 2017
for dtype in data embedding MC;
    do cmsRun Kappa/Skimming/python/postMiniAODSequences.py year=2017 dtype=${dtype}
done;

# year 2018
for dtype in data data-prompt embedding MC;
    do cmsRun Kappa/Skimming/python/postMiniAODSequences.py year=2018 dtype=${dtype}
done;
