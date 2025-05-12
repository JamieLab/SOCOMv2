#!/usr/bin/env python3

run_fluxes = False
run_file_generation = True
run_plots = True
if run_fluxes:
    import SOCOMv2_setup_model_flux
    import SOCOMv2_setup_dataproduct_flux

if run_file_generation:
    import SOCOMv2_combine_final_csv
    import SOCOMv2_consistent_grid
    import SOCOMv2_model_a_value
    import SOCOMv2_model_kw_append

if run_plots:
    import SOCOMv2_plot_model
