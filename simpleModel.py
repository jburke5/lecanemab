# take the general effect of amyloid lowering -> improved cognition rom the meta0analysis 
# Ackley SF, Zimmerman SC, Brenowitz WD, Tchetgen EJT, Gold AL, Manly JJ, Mayeda ER, Filshtein TJ, Power MC, Elahi FM, Brickman AM, Glymour MM. Effect of reductions in amyloid levels on cognitive change in randomized trials: instrumental variable meta-analysis. Bmj. 2021;372:n156.

## redtag - make sure to get the updated version of this that added teh extra data, there is an errata to the initial paper

# for all da

# this will give us change in amyloid lowering -> MMSE

allDataSUVRToMMSEMean = 0.034
allDataSUVRToMMSESE = 0.046

amyloidSUVRTToMMSEMean = 0.044
amyloidSUVRTToMMSESE = 0.049

# it looks like they have an version of this that uses CDR-SB in their appendix
# it also looks like they have an updated version of the analysis on their shiny app: https://amyloidintegratingevidence.shinyapps.io/Shiny/ 

# generate a prior — multiply the eneral effect by the distribution fo that association to get the expected effect of lecanemab
# redtag: need to clarify what SUVR means...going to assume that # going to assume that their degree of amyloid in % change in centiloids transfers to SUVR

# not sure if this should be on a relative scale or an absolute one
changeIn18MonthSUVRMean = 55.5
changeIn18MonthSUVRSE = 1.80

averageBaselineCentiloids = 76.5

# this represents data from the lecanemab trial on the SURV reduction, in 0.1 unit SUR
relativeChangeIn18MonthSUVRMean = changeIn18MonthSUVRMean/averageBaselineCentiloids*10
relativeChangeIn18MonthSUVRSE = changeIn18MonthSUVRSE/averageBaselineCentiloids*10

mmseToCDRSBIntercept = 30
mmseToCDRSBSlope = (20.75-30)/6.25

cdrToMMSEIntercept = -1*  mmseToCDRSBIntercept
cdrToMMSEslope = 1/mmseToCDRSBSlope
print(f"mmse to CRDR slope : {mmseToCDRSBSlope}")

# update the prior using the observed effect from the lecanemab trial...to get a posterior

meanCDRSBChangeWithLecanemabInTrial=-0.45
sdCDRSBChangeWithLecanemabInTrial=0.11

import numpy as np
import pymc as pm

trials = 10; successes = 5

# 1. surv to MMSE from paper
# 2. SUVR to CDR-SB from paper appendix
# 3. SURV to CDR-SB * lecanemabic SUVR change
# 5. lecanemab trial data on CDR-SB


## MESS UP TAG — I LEFT OFF HERE...

## i think the problem is that i have the linear equation fucked up, i might have it backwards?



import arviz as az

#az.plot_posterior(idata, show=True);

print(f"mmse over SUVR, mean: {allDataSUVRToMMSEMean}, SE: {allDataSUVRToMMSESE}")
print(f"lecanemab SUVR change: {relativeChangeIn18MonthSUVRMean}, SE: {relativeChangeIn18MonthSUVRSE}")

print(f"lecanemab CDR change (likelihood): {meanCDRSBChangeWithLecanemabInTrial}, SE: {sdCDRSBChangeWithLecanemabInTrial}")


with pm.Model() as model:
	# this represents the effect from the meta-analysis, quantifying how a given SUVR change leads to a MMSE change in units of MMSE points / 0.1 unit SUVR reduction
	# it is a random variale accounting for the error in the MMSE-SUVR relationship from prior trials
	mmseOverSUVR = pm.Normal('mmseOverSUVR', mu=allDataSUVRToMMSEMean, sigma =allDataSUVRToMMSESE)

	# this represents data from the lecanemab trial on the SUVR reduction, in 0.1 unit SUR 
	# it is a random variale accounting for the error in the magnitude of SUVR reduction in the trial
	lecanemabSUVRChange = pm.Normal('lecanemabSUVRChange', mu=relativeChangeIn18MonthSUVRMean, sigma =relativeChangeIn18MonthSUVRSE)

	# this is a deterministic variale that multiplies the SUVR/MMSE to estimate the effect of lecanemab on MMSE
	#lecanemabMMSEMean = pm.Deterministic('lecanemabMMSEMean', lecanemabSUVRChange*mmseOverSUVR)
	#lecanemabMMSESE = pm.Deterministic('lecanemabMMSESE', pm.math.sqrt(pm.math.sqr(relativeChangeIn18MonthSUVRSE)/lecanemabSUVRChange + pm.math.sqr(allDataSUVRToMMSESE/mmseOverSUVR)))
	#lecanemabMMSEEffect = pm.Normal('lecanemabMMSEEffect', mu=lecanemabMMSEMean, sigma=lecanemabMMSESE)
	lecanemabMMSEEffect = pm.Deterministic('lecanemabMMSEEffect', lecanemabSUVRChange*mmseOverSUVR)

	# this represents our prior — linearly scaling the predicted lecanemab CDR effect to MMSE
	#lecanemabCDRSE = pm.Deterministic('lecanemabCDRSE', lecanemabMMSESE/mmseToCDRSBSlope)
	#lecanemabCDRMean=lecanemabMMSEMean/mmseToCDRSBSlope
	#lecanemabCDREffect = pm.Normal('lecanemabCDREffect', mu=lecanemabCDRMean, sigma=lecanemabCDRSE)
	lecanemabCDREffect = pm.Deterministic('lecanemabCDREffect', lecanemabMMSEEffect/mmseToCDRSBSlope)


	#priorSE = pm.Deterministic('priorSE', pm.math.sqrt(pm.math.sqr(relativeChangeIn18MonthSUVRSE)/relativeChangeIn18MonthSUVRMean + pm.math.sqr(allDataSUVRToMMSESE)/allDataSUVRToMMSEMean))
	#priorMean = pm.Deterministic('priorMean', suvrToCDR * lecanemabSUVRChange)
	#prior = pm.Normal('prior', mu=priorMean, sigma= priorSE)

	cdrChangeWithTreatment = pm.Normal('cdrChangeWithTreatment', mu=meanCDRSBChangeWithLecanemabInTrial, sigma=sdCDRSBChangeWithLecanemabInTrial)
	#posteriorMean = pm.Deterministic('posteriorMean', (lecanemabCDREffect+likelihood)/2)
	#posteriorSE = pm.Deterministic('posteriorSE', pm.math.sqrt(pm.math.sqr(lecanemabCDRSE)/lecanemabCDRMean + pm.math.sqr(sdCDRSBChangeWithLecanemabInTrial/meanCDRSBChangeWithLecanemabInTrial)))
	#posterior = pm.Normal('posterior', mu=lecanemabCDREffect.mean(), sigma=lecanemabCDREffect.std(), observed=likelihood)
	posterior = pm.Potential('posterior', lecanemabCDREffect*cdrChangeWithTreatment)
	
    
if __name__ == "__main__":
    with model:
        trace = pm.sample (2000,tune=1000, cores=1) 
        print(az.summary(trace, kind="stats"))
        

