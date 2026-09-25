# Historical Mg charge distribution

`MgOChargeProbabilityDistributionFactoryObject` creates the uniform
`Mg.charge` distribution consumed by the PyFlamestk MgO serial-uniform
reconstruction. The bounds `1.5` and `2.5` come from the pinned
`pyposmat.potential` evidence, SHA-256
`bb6bb6461468c96012acfa298bd1fc473d771d3ce82f1c4effed662e9ffa1e1d`.
The maintained composition selects
`ProbabilityDistributionSamplerAdapter.NUMPY`.

Fast tests check the exact consumer configuration. An opt-in statistical
validation test lives beside this consumer and invokes the reusable uniform
sampler validator.
