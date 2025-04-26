clear all
set seed 12345

**** SIMULATION PROGRAM WITH FRACTIONAL OUTCOMES ****
capture program drop incarceration_sim_frac
program define incarceration_sim_frac, rclass
    // Input parameters
    args i_size        /* Size of group i (inconsistently categorized) */ ///
         inc_rate_i    /* Incarceration rate for group i */
         
    // Fixed incarceration rates for stable groups
    local inc_rate_w = 0.001  // 100/100K for stable White population
    local inc_rate_b = 0.005  // 500/100K for stable Black population
    
    // Preserve current dataset
    preserve
    
    // Setup population numbers (maintain 5:1 white:black ratio excluding group i)
    local b_ratio = 1
    local w_ratio = 5
    local ratio_total = `b_ratio' + `w_ratio'
    
    local remain_pop = 10000 - `i_size'
    local b_stable = round(`remain_pop' * (`b_ratio'/`ratio_total'))
    local w_stable = round(`remain_pop' * (`w_ratio'/`ratio_total'))
    
    // Double-check and adjust if needed
    if `b_stable' + `w_stable' != `remain_pop' {
        local w_stable = `remain_pop' - `b_stable'
    }
    
    // Create dataset with individual records
    clear
    set obs 10000
    
    // Assign true group membership (0=white stable, 1=black stable, 2=group i)
    gen true_group = 0 if _n <= `w_stable'
    replace true_group = 1 if _n > `w_stable' & _n <= (`w_stable' + `b_stable')
    replace true_group = 2 if _n > (`w_stable' + `b_stable')
    
    // Assign observed race (0=white, 1=black)
    gen black = (true_group == 1)  // All true blacks are observed as black
    replace black = 0 if true_group == 0  // All true whites are observed as white
    
    // Group i is split 50/50 between black and white - using fractional assignment
    gen prob_black = 0.5 if true_group == 2  // Probability of being categorized as black
    replace black = prob_black if true_group == 2  // Use fractional outcome
    
    // Assign incarceration status (fractional)
    gen incarcerated = `inc_rate_w' if true_group == 0  // Exact rate for white stable
    replace incarcerated = `inc_rate_b' if true_group == 1  // Exact rate for black stable
    replace incarcerated = `inc_rate_i' if true_group == 2  // Exact rate for group i
    
    // Calculate true incarceration rates by real group
    quietly summarize incarcerated if true_group == 0
    local white_true_inc_rate = r(mean)
    
    quietly summarize incarcerated if true_group == 1
    local black_true_inc_rate = r(mean)
    
    quietly summarize incarcerated if true_group == 2
    local group_i_inc_rate = r(mean)
    
    // Calculate observed incarceration rates by observed race
    // For fractional outcomes, this requires weighted calculations
    
    // For observed black group
    gen black_inc_product = black * incarcerated  // For each person: P(black) * P(incarcerated)
    quietly sum black_inc_product
    local black_inc_total = r(sum)
    quietly sum black
    local black_total = r(sum)
    local observed_black_inc_rate = `black_inc_total' / `black_total'
    
    // For observed white group
    gen white = 1 - black  // Probability of being white
    gen white_inc_product = white * incarcerated  // For each person: P(white) * P(incarcerated)
    quietly sum white_inc_product
    local white_inc_total = r(sum)
    quietly sum white
    local white_total = r(sum)
    local observed_white_inc_rate = `white_inc_total' / `white_total'
    
    // Calculate observed racial disparity
    local observed_inc_ratio = `observed_black_inc_rate'/`observed_white_inc_rate'
    
    // Calculate true racial disparity (excluding group i)
    local true_inc_ratio = `black_true_inc_rate'/`white_true_inc_rate'
    
    // Calculate bias due to inconsistent categorization
    local ratio_bias = `observed_inc_ratio' - `true_inc_ratio'
    local ratio_bias_pct = 100*(`observed_inc_ratio' - `true_inc_ratio')/`true_inc_ratio'
    
    // Calculate proportion of each observed group - using fractional values
    quietly sum black
    local observed_black_n = r(sum)
    quietly sum white
    local observed_white_n = r(sum)
    
    // Calculate what percent of each observed racial category is from group i
    gen is_group_i = (true_group == 2)
    gen black_group_i = black * is_group_i
    quietly sum black_group_i
    local black_from_i = r(sum)
    local i_in_black_pct = 100 * `black_from_i' / `observed_black_n'
    
    gen white_group_i = white * is_group_i
    quietly sum white_group_i
    local white_from_i = r(sum)
    local i_in_white_pct = 100 * `white_from_i' / `observed_white_n'
    
    // Return results
    return scalar true_inc_ratio = `true_inc_ratio'
    return scalar observed_inc_ratio = `observed_inc_ratio'
    return scalar ratio_bias = `ratio_bias'
    return scalar ratio_bias_pct = `ratio_bias_pct'
    
    return scalar white_true_inc_rate = `white_true_inc_rate'
    return scalar black_true_inc_rate = `black_true_inc_rate'
    return scalar group_i_inc_rate = `group_i_inc_rate'
    return scalar observed_black_inc_rate = `observed_black_inc_rate'
    return scalar observed_white_inc_rate = `observed_white_inc_rate'
    
    return scalar i_size = `i_size'
    return scalar i_size_pct = 100*`i_size'/10000
    return scalar i_in_black_pct = `i_in_black_pct'
    return scalar i_in_white_pct = `i_in_white_pct'
    
    return scalar observed_black_pct = 100*`observed_black_n'/10000
    return scalar observed_white_pct = 100*`observed_white_n'/10000
    
    // Restore original dataset
    restore
end

**** RUNNING SIMULATIONS USING POSTFILE ****

// Set up output file
tempfile sim_results
postfile sim_handle i_size i_size_pct inc_rate_i ///
                   true_inc_ratio observed_inc_ratio ratio_bias ratio_bias_pct ///
                   white_true_inc_rate black_true_inc_rate group_i_inc_rate ///
                   observed_black_inc_rate observed_white_inc_rate ///
                   i_in_black_pct i_in_white_pct ///
                   observed_black_pct observed_white_pct ///
                   using "`sim_results'", replace

// Run 10,000 simulations with random parameters
forvalues i = 1/10000 {
    // Generate random parameter values within realistic ranges
    local i_size = round(runiform(0, 5000))     // Size of group i (0-50% of population)
    local inc_rate_i = runiform(0.0005, 0.01)    // Incarceration rate for group i
    
    // Run simulation with these parameters
    qui incarceration_sim_frac `i_size' `inc_rate_i'
    
    // Store results
    post sim_handle (r(i_size)) (r(i_size_pct)) (`inc_rate_i') ///
                   (r(true_inc_ratio)) (r(observed_inc_ratio)) ///
                   (r(ratio_bias)) (r(ratio_bias_pct)) ///
                   (r(white_true_inc_rate)) (r(black_true_inc_rate)) (r(group_i_inc_rate)) ///
                   (r(observed_black_inc_rate)) (r(observed_white_inc_rate)) ///
                   (r(i_in_black_pct)) (r(i_in_white_pct)) ///
                   (r(observed_black_pct)) (r(observed_white_pct))
}

// Close postfile and load results
postclose sim_handle
use "`sim_results'", clear

// Format variables for easier display
format inc_rate_i %5.3f
format observed_inc_ratio true_inc_ratio ratio_bias %4.2f
format ratio_bias_pct i_in_black_pct i_in_white_pct observed_black_pct observed_white_pct %4.1f

// Display summary statistics
summarize

// Verify that inc_rate_i exactly equals group_i_inc_rate in this fractional approach
gen inc_rate_diff = inc_rate_i - group_i_inc_rate
summarize inc_rate_diff, detail  // Should be zero

// Basic histograms of observed ratios
*histogram observed_inc_ratio, bin(30) color(blue%50) normal ///
    title("Distribution of Observed Black/White Incarceration Ratios") ///
    xtitle("Black/White Incarceration Ratio") ///
    name(hist_observed, replace)

// Explore relationship between group i size and observed disparity
twoway (scatter observed_inc_ratio i_size_pct) (lowess observed_inc_ratio i_size_pct), ///
    title("Effect of Inconsistently Categorized Group Size on Racial Disparity") ///
    xtitle("Group i as % of Population") ///
    ytitle("Observed Black/White Incarceration Ratio") ///
    name(I_Size_2, replace) ///
    legend(off)

// Look at how the observed racial disparity changes with group i's incarceration rate
twoway (scatter observed_inc_ratio inc_rate_i) (lowess observed_inc_ratio inc_rate_i), ///
    title("Effect of Group i's Incarceration Rate on Racial Disparity") ///
    xtitle("Incarceration Rate of Group i") ///
    ytitle("Observed Black/White Incarceration Ratio") ///
    name(I_Rate_2, replace) ///
    legend(off)
	
gen i_size_pct_sq = i_size_pct^2
	
regress observed_inc_ratio inc_rate_i i_size_pct c.inc_rate_i#c.i_size_pct i_size_pct_sq 

**** SIMULATION PROGRAM: I's CATEGORIZATION MATCHES THE RATIO OF W:B IN THE POPULATION 

clear all
set seed 12345

capture program drop incarceration_sim_frac
program define incarceration_sim_frac, rclass
    // Input parameters
    args i_size        /* Size of group i (inconsistently categorized) */ ///
         inc_rate_i    /* Incarceration rate for group i */
         
    // Fixed incarceration rates for stable groups
    local inc_rate_w = 0.001  // 1% for stable White population
    local inc_rate_b = 0.005  // 5% for stable Black population
    
    // Preserve current dataset
    preserve
    
    // Setup population numbers (maintain 5:1 white:black ratio excluding group i)
    local b_ratio = 1
    local w_ratio = 5
    local ratio_total = `b_ratio' + `w_ratio'
    
    local remain_pop = 10000 - `i_size'
    local b_stable = round(`remain_pop' * (`b_ratio'/`ratio_total'))
    local w_stable = round(`remain_pop' * (`w_ratio'/`ratio_total'))
    
    // Double-check and adjust if needed
    if `b_stable' + `w_stable' != `remain_pop' {
        local w_stable = `remain_pop' - `b_stable'
    }
    
    // Create dataset with individual records
    clear
    set obs 10000
    
    // Assign true group membership (0=white stable, 1=black stable, 2=group i)
    gen true_group = 0 if _n <= `w_stable'
    replace true_group = 1 if _n > `w_stable' & _n <= (`w_stable' + `b_stable')
    replace true_group = 2 if _n > (`w_stable' + `b_stable')
    
    // Assign observed race (0=white, 1=black)
    gen black = (true_group == 1)  // All true blacks are observed as black
    replace black = 0 if true_group == 0  // All true whites are observed as white
    
    // Group i is split 17-83 between black and white 
    gen prob_black = 0.1666667 if true_group == 2  // Probability of being categorized as black
    replace black = prob_black if true_group == 2  // Use fractional outcome
    
    // Assign incarceration status (fractional)
    gen incarcerated = `inc_rate_w' if true_group == 0  // Exact rate for white stable
    replace incarcerated = `inc_rate_b' if true_group == 1  // Exact rate for black stable
    replace incarcerated = `inc_rate_i' if true_group == 2  // Exact rate for group i
    
    // Calculate true incarceration rates by real group
    quietly summarize incarcerated if true_group == 0
    local white_true_inc_rate = r(mean)
    
    quietly summarize incarcerated if true_group == 1
    local black_true_inc_rate = r(mean)
    
    quietly summarize incarcerated if true_group == 2
    local group_i_inc_rate = r(mean)
    
    // Calculate observed incarceration rates by observed race
    // For fractional outcomes, this requires weighted calculations
    
    // For observed black group
    gen black_inc_product = black * incarcerated  // For each person: P(black) * P(incarcerated)
    quietly sum black_inc_product
    local black_inc_total = r(sum)
    quietly sum black
    local black_total = r(sum)
    local observed_black_inc_rate = `black_inc_total' / `black_total'
    
    // For observed white group
    gen white = 1 - black  // Probability of being white
    gen white_inc_product = white * incarcerated  // For each person: P(white) * P(incarcerated)
    quietly sum white_inc_product
    local white_inc_total = r(sum)
    quietly sum white
    local white_total = r(sum)
    local observed_white_inc_rate = `white_inc_total' / `white_total'
    
    // Calculate observed racial disparity
    local observed_inc_ratio = `observed_black_inc_rate'/`observed_white_inc_rate'
    
    // Calculate true racial disparity (excluding group i)
    local true_inc_ratio = `black_true_inc_rate'/`white_true_inc_rate'
    
    // Calculate bias due to inconsistent categorization
    local ratio_bias = `observed_inc_ratio' - `true_inc_ratio'
    local ratio_bias_pct = 100*(`observed_inc_ratio' - `true_inc_ratio')/`true_inc_ratio'
    
    // Calculate proportion of each observed group - using fractional values
    quietly sum black
    local observed_black_n = r(sum)
    quietly sum white
    local observed_white_n = r(sum)
    
    // Calculate what percent of each observed racial category is from group i
    gen is_group_i = (true_group == 2)
    gen black_group_i = black * is_group_i
    quietly sum black_group_i
    local black_from_i = r(sum)
    local i_in_black_pct = 100 * `black_from_i' / `observed_black_n'
    
    gen white_group_i = white * is_group_i
    quietly sum white_group_i
    local white_from_i = r(sum)
    local i_in_white_pct = 100 * `white_from_i' / `observed_white_n'
    
    // Return results
    return scalar true_inc_ratio = `true_inc_ratio'
    return scalar observed_inc_ratio = `observed_inc_ratio'
    return scalar ratio_bias = `ratio_bias'
    return scalar ratio_bias_pct = `ratio_bias_pct'
    
    return scalar white_true_inc_rate = `white_true_inc_rate'
    return scalar black_true_inc_rate = `black_true_inc_rate'
    return scalar group_i_inc_rate = `group_i_inc_rate'
    return scalar observed_black_inc_rate = `observed_black_inc_rate'
    return scalar observed_white_inc_rate = `observed_white_inc_rate'
    
    return scalar i_size = `i_size'
    return scalar i_size_pct = 100*`i_size'/10000
    return scalar i_in_black_pct = `i_in_black_pct'
    return scalar i_in_white_pct = `i_in_white_pct'
    
    return scalar observed_black_pct = 100*`observed_black_n'/10000
    return scalar observed_white_pct = 100*`observed_white_n'/10000
    
    // Restore original dataset
    restore
end

**** RUNNING SIMULATIONS USING POSTFILE ****

// Set up output file
tempfile sim_results
postfile sim_handle i_size i_size_pct inc_rate_i ///
                   true_inc_ratio observed_inc_ratio ratio_bias ratio_bias_pct ///
                   white_true_inc_rate black_true_inc_rate group_i_inc_rate ///
                   observed_black_inc_rate observed_white_inc_rate ///
                   i_in_black_pct i_in_white_pct ///
                   observed_black_pct observed_white_pct ///
                   using "`sim_results'", replace

// Run 10,000 simulations with random parameters
forvalues i = 1/10000 {
    // Generate random parameter values within realistic ranges
    local i_size = round(runiform(0, 5000))     // Size of group i (0-50% of population)
    local inc_rate_i = runiform(0.0005, 0.01)    // Incarceration rate for group i
    
    // Run simulation with these parameters
    qui incarceration_sim_frac `i_size' `inc_rate_i'
    
    // Store results
    post sim_handle (r(i_size)) (r(i_size_pct)) (`inc_rate_i') ///
                   (r(true_inc_ratio)) (r(observed_inc_ratio)) ///
                   (r(ratio_bias)) (r(ratio_bias_pct)) ///
                   (r(white_true_inc_rate)) (r(black_true_inc_rate)) (r(group_i_inc_rate)) ///
                   (r(observed_black_inc_rate)) (r(observed_white_inc_rate)) ///
                   (r(i_in_black_pct)) (r(i_in_white_pct)) ///
                   (r(observed_black_pct)) (r(observed_white_pct))
}

// Close postfile and load results
postclose sim_handle
use "`sim_results'", clear

// Format variables for easier display
format inc_rate_i %5.3f
format observed_inc_ratio true_inc_ratio ratio_bias %4.2f
format ratio_bias_pct i_in_black_pct i_in_white_pct observed_black_pct observed_white_pct %4.1f

// Display summary statistics
summarize

// Verify that inc_rate_i exactly equals group_i_inc_rate in this fractional approach
gen inc_rate_diff = inc_rate_i - group_i_inc_rate
summarize inc_rate_diff, detail  // Should be zero

// Basic histograms of observed ratios
*histogram observed_inc_ratio, bin(30) color(blue%50) normal ///
    title("Distribution of Observed Black/White Incarceration Ratios") ///
    xtitle("Black/White Incarceration Ratio") ///
    name(hist_observed, replace)

// Explore relationship between group i size and observed disparity
twoway (scatter observed_inc_ratio i_size_pct) (lowess observed_inc_ratio i_size_pct), ///
    title("Effect of Inconsistently Categorized Group Size on Racial Disparity") ///
    xtitle("Group i as % of Population") ///
    ytitle("Observed Black/White Incarceration Ratio") ///
    name(I_Size_2, replace) ///
    legend(off)

// Look at how the observed racial disparity changes with group i's incarceration rate
twoway (scatter observed_inc_ratio inc_rate_i) (lowess observed_inc_ratio inc_rate_i), ///
    title("Effect of Group i's Incarceration Rate on Racial Disparity") ///
    xtitle("Incarceration Rate of Group i") ///
    ytitle("Observed Black/White Incarceration Ratio") ///
    name(I_Rate_2, replace) ///
    legend(off)
	
gen i_size_pct_sq = i_size_pct^2

regress observed_inc_ratio inc_rate_i i_size_pct c.inc_rate_i#c.i_size_pct i_size_pct_sq 


clear all
set seed 12345

**** SIMULATION PROGRAM WITH VARIABLE CATEGORIZATION ****
capture program drop incarceration_sim_frac
program define incarceration_sim_frac, rclass
    // Input parameters
    args i_size        /* Size of group i (inconsistently categorized) */ ///
         inc_rate_i    /* Incarceration rate for group i */ ///
         i_black_pct   /* Percentage of group i categorized as Black (0-100) */
         
    // Convert percentage to proportion
    local i_black_prop = `i_black_pct' / 100
    
    // Fixed incarceration rates for stable groups
    local inc_rate_w = 0.01  // 1% for stable White population
    local inc_rate_b = 0.05  // 5% for stable Black population
    
    // Preserve current dataset
    preserve
    
    // Setup population numbers (maintain 5:1 white:black ratio excluding group i)
    local b_ratio = 1
    local w_ratio = 5
    local ratio_total = `b_ratio' + `w_ratio'
    
    local remain_pop = 10000 - `i_size'
    local b_stable = round(`remain_pop' * (`b_ratio'/`ratio_total'))
    local w_stable = round(`remain_pop' * (`w_ratio'/`ratio_total'))
    
    // Double-check and adjust if needed
    if `b_stable' + `w_stable' != `remain_pop' {
        local w_stable = `remain_pop' - `b_stable'
    }
    
    // Create dataset with individual records
    clear
    set obs 10000
    
    // Assign true group membership (0=white stable, 1=black stable, 2=group i)
    gen true_group = 0 if _n <= `w_stable'
    replace true_group = 1 if _n > `w_stable' & _n <= (`w_stable' + `b_stable')
    replace true_group = 2 if _n > (`w_stable' + `b_stable')
    
    // Assign observed race (0=white, 1=black)
    gen black = (true_group == 1)  // All true blacks are observed as black
    replace black = 0 if true_group == 0  // All true whites are observed as white
    
    // Group i's racial categorization based on input parameter
    gen prob_black = `i_black_prop' if true_group == 2  // Probability of being categorized as black
    replace black = prob_black if true_group == 2  // Use fractional outcome
    
    // Assign incarceration status (fractional)
    gen incarcerated = `inc_rate_w' if true_group == 0  // Exact rate for white stable
    replace incarcerated = `inc_rate_b' if true_group == 1  // Exact rate for black stable
    replace incarcerated = `inc_rate_i' if true_group == 2  // Exact rate for group i
    
    // Calculate true incarceration rates by real group
    quietly summarize incarcerated if true_group == 0
    local white_true_inc_rate = r(mean)
    
    quietly summarize incarcerated if true_group == 1
    local black_true_inc_rate = r(mean)
    
    quietly summarize incarcerated if true_group == 2
    local group_i_inc_rate = r(mean)
    
    // Calculate observed incarceration rates by observed race
    // For fractional outcomes, this requires weighted calculations
    
    // For observed black group
    gen black_inc_product = black * incarcerated  // For each person: P(black) * P(incarcerated)
    quietly sum black_inc_product
    local black_inc_total = r(sum)
    quietly sum black
    local black_total = r(sum)
    local observed_black_inc_rate = `black_inc_total' / `black_total'
    
    // For observed white group
    gen white = 1 - black  // Probability of being white
    gen white_inc_product = white * incarcerated  // For each person: P(white) * P(incarcerated)
    quietly sum white_inc_product
    local white_inc_total = r(sum)
    quietly sum white
    local white_total = r(sum)
    local observed_white_inc_rate = `white_inc_total' / `white_total'
    
    // Calculate observed racial disparity
    local observed_inc_ratio = `observed_black_inc_rate'/`observed_white_inc_rate'
    
    // Calculate true racial disparity (excluding group i)
    local true_inc_ratio = `black_true_inc_rate'/`white_true_inc_rate'
    
    // Calculate bias due to inconsistent categorization
    local ratio_bias = `observed_inc_ratio' - `true_inc_ratio'
    local ratio_bias_pct = 100*(`observed_inc_ratio' - `true_inc_ratio')/`true_inc_ratio'
    
    // Calculate proportion of each observed group - using fractional values
    quietly sum black
    local observed_black_n = r(sum)
    quietly sum white
    local observed_white_n = r(sum)
    
    // Calculate what percent of each observed racial category is from group i
    gen is_group_i = (true_group == 2)
    gen black_group_i = black * is_group_i
    quietly sum black_group_i
    local black_from_i = r(sum)
    local i_in_black_pct = 100 * `black_from_i' / `observed_black_n'
    
    gen white_group_i = white * is_group_i
    quietly sum white_group_i
    local white_from_i = r(sum)
    local i_in_white_pct = 100 * `white_from_i' / `observed_white_n'
    
    // Return results
    return scalar true_inc_ratio = `true_inc_ratio'
    return scalar observed_inc_ratio = `observed_inc_ratio'
    return scalar ratio_bias = `ratio_bias'
    return scalar ratio_bias_pct = `ratio_bias_pct'
    
    return scalar white_true_inc_rate = `white_true_inc_rate'
    return scalar black_true_inc_rate = `black_true_inc_rate'
    return scalar group_i_inc_rate = `group_i_inc_rate'
    return scalar observed_black_inc_rate = `observed_black_inc_rate'
    return scalar observed_white_inc_rate = `observed_white_inc_rate'
    
    return scalar i_size = `i_size'
    return scalar i_size_pct = 100*`i_size'/10000
    return scalar i_black_pct = `i_black_pct'
    return scalar i_in_black_pct = `i_in_black_pct'
    return scalar i_in_white_pct = `i_in_white_pct'
    
    return scalar observed_black_pct = 100*`observed_black_n'/10000
    return scalar observed_white_pct = 100*`observed_white_n'/10000
    
    // Restore original dataset
    restore
end

**** RUNNING SIMULATIONS USING POSTFILE ****

// Set up output file
tempfile sim_results
postfile sim_handle i_size i_size_pct i_black_pct inc_rate_i ///
                   true_inc_ratio observed_inc_ratio ratio_bias ratio_bias_pct ///
                   white_true_inc_rate black_true_inc_rate group_i_inc_rate ///
                   observed_black_inc_rate observed_white_inc_rate ///
                   i_in_black_pct i_in_white_pct ///
                   observed_black_pct observed_white_pct ///
                   using "`sim_results'", replace

// Run 10,000 simulations with random parameters
forvalues i = 1/10000 {
    // Generate random parameter values within realistic ranges
    local i_size = round(runiform(0, 5000))      // Size of group i (0-50% of population)
    local inc_rate_i = runiform(0.005, 0.10)     // Incarceration rate for group i
    local i_black_pct = runiform(0, 100)         // Random % of group i categorized as Black (0-100%)
    
    // Run simulation with these parameters
    qui incarceration_sim_frac `i_size' `inc_rate_i' `i_black_pct'
    
    // Store results
    post sim_handle (r(i_size)) (r(i_size_pct)) (r(i_black_pct)) (`inc_rate_i') ///
                   (r(true_inc_ratio)) (r(observed_inc_ratio)) ///
                   (r(ratio_bias)) (r(ratio_bias_pct)) ///
                   (r(white_true_inc_rate)) (r(black_true_inc_rate)) (r(group_i_inc_rate)) ///
                   (r(observed_black_inc_rate)) (r(observed_white_inc_rate)) ///
                   (r(i_in_black_pct)) (r(i_in_white_pct)) ///
                   (r(observed_black_pct)) (r(observed_white_pct))
}

// Close postfile and load results
postclose sim_handle
use "`sim_results'", clear

// Format variables for easier display
format inc_rate_i %5.4f
format observed_inc_ratio true_inc_ratio ratio_bias %4.2f
format ratio_bias_pct i_in_black_pct i_in_white_pct observed_black_pct observed_white_pct i_black_pct %4.1f

// Display summary statistics
summarize

// Verify that inc_rate_i exactly equals group_i_inc_rate in this fractional approach
gen inc_rate_diff = inc_rate_i - group_i_inc_rate
summarize inc_rate_diff, detail  // Should be zero

// Basic histograms of observed ratios
*histogram observed_inc_ratio, bin(30) color(blue%50) normal ///
    title("Distribution of Observed Black/White Incarceration Ratios") ///
    xtitle("Black/White Incarceration Ratio") ///
    name(hist_observed, replace)

// Explore relationship between group i size and observed disparity
twoway (scatter observed_inc_ratio i_size_pct) (lowess observed_inc_ratio i_size_pct), ///
    title("Effect of Inconsistently Categorized Group Size on Racial Disparity") ///
    xtitle("Group i as % of Population") ///
    ytitle("Observed Black/White Incarceration Ratio") ///
    name(scatter_size_3, replace) ///
    legend(off)

// Look at how the observed racial disparity changes with group i's incarceration rate
twoway (scatter observed_inc_ratio inc_rate_i) (lowess observed_inc_ratio inc_rate_i), ///
    title("Effect of Group i's Incarceration Rate on Racial Disparity") ///
    xtitle("Incarceration Rate of Group i") ///
    ytitle("Observed Black/White Incarceration Ratio") ///
    name(scatter_inc_3, replace) ///
    legend(off)

// New plot: Effect of % of group i categorized as Black on racial disparity
twoway (scatter observed_inc_ratio i_black_pct) (lowess observed_inc_ratio i_black_pct), ///
    title("Effect of Group i's Black Categorization on Racial Disparity") ///
    xtitle("% of Group i Categorized as Black") ///
    ytitle("Observed Black/White Incarceration Ratio") ///
    name(scatter_black_pct, replace) ///
    legend(off)

// Generate categories for group i size
gen i_size_cat = "None" if i_size_pct == 0
replace i_size_cat = "Small (1-10%)" if i_size_pct > 0 & i_size_pct <= 10
replace i_size_cat = "Medium (10-25%)" if i_size_pct > 10 & i_size_pct <= 25
replace i_size_cat = "Large (25-50%)" if i_size_pct > 25 & i_size_pct <= 50

// Generate categories for group i Black categorization
gen i_black_cat = "Mostly White (0-25%)" if i_black_pct <= 25
replace i_black_cat = "Mixed (25-75%)" if i_black_pct > 25 & i_black_pct < 75
replace i_black_cat = "Mostly Black (75-100%)" if i_black_pct >= 75

// Look at how the observed racial disparity changes with group i's incarceration rate
// for different sizes of group i
*twoway (scatter observed_inc_ratio inc_rate_i if i_size_cat=="Small (1-10%)", msize(small) mcolor(green%30)) ///
       (scatter observed_inc_ratio inc_rate_i if i_size_cat=="Medium (10-25%)", msize(small) mcolor(orange%30)) ///
       (scatter observed_inc_ratio inc_rate_i if i_size_cat=="Large (25-50%)", msize(small) mcolor(red%30)) ///
       (lowess observed_inc_ratio inc_rate_i if i_size_cat=="None", lcolor(blue) lwidth(medthick)) ///
       (lowess observed_inc_ratio inc_rate_i if i_size_cat=="Small (1-10%)", lcolor(green) lwidth(medthick)) ///
       (lowess observed_inc_ratio inc_rate_i if i_size_cat=="Medium (10-25%)", lcolor(orange) lwidth(medthick)) ///
       (lowess observed_inc_ratio inc_rate_i if i_size_cat=="Large (25-50%)", lcolor(red) lwidth(medthick)), ///
       title("Effect of Inconsistent Categorization on Racial Disparity") ///
       ytitle("Observed Black:White Incarceration Ratio") ///
       xtitle("Incarceration Rate of Group i") ///
       legend(order(5 "Group i 1-10%" 6 "Group i 10-25%" 7 "Group i 25-50%")) ///
       yline(5, lpattern(dash) lcolor(black)) ///
       name(disparity_inc_by_size, replace)

// Look at how racial categorization affects disparity by group i size
*twoway (scatter observed_inc_ratio i_black_pct if i_size_cat=="Small (1-10%)", msize(small) mcolor(green%30)) ///
       (scatter observed_inc_ratio i_black_pct if i_size_cat=="Medium (10-25%)", msize(small) mcolor(orange%30)) ///
       (scatter observed_inc_ratio i_black_pct if i_size_cat=="Large (25-50%)", msize(small) mcolor(red%30)) ///
       (lowess observed_inc_ratio i_black_pct if i_size_cat=="Small (1-10%)", lcolor(green) lwidth(medthick)) ///
       (lowess observed_inc_ratio i_black_pct if i_size_cat=="Medium (10-25%)", lcolor(orange) lwidth(medthick)) ///
       (lowess observed_inc_ratio i_black_pct if i_size_cat=="Large (25-50%)", lcolor(red) lwidth(medthick)), ///
       title("Effect of Group i's Racial Categorization on Disparity") ///
       ytitle("Observed Black:White Incarceration Ratio") ///
       xtitle("% of Group i Categorized as Black") ///
       legend(order(4 "Group i 1-10%" 5 "Group i 10-25%" 6 "Group i 25-50%")) ///
       yline(5, lpattern(dash) lcolor(black)) ///
       name(disparity_by_black_pct, replace)

// Look at how racial categorization affects disparity by i's incarceration rate
twoway (scatter observed_inc_ratio inc_rate_i if i_black_pct <= 20, msize(small) mcolor(green%20)) ///
       (scatter observed_inc_ratio inc_rate_i if i_black_pct > 20 & i_black_pct <= 40, msize(small) mcolor(orange%20)) ///
       (scatter observed_inc_ratio inc_rate_i if i_black_pct > 40 & i_black_pct <= 60, msize(small) mcolor(red%20)) ///
       (scatter observed_inc_ratio inc_rate_i if i_black_pct > 60 & i_black_pct <= 80, msize(small) mcolor(blue%20)) ///
       (scatter observed_inc_ratio inc_rate_i if i_black_pct > 80, msize(small) mcolor(purple%20)) ///
       (lowess observed_inc_ratio inc_rate_i if i_black_pct <= 20, lcolor(green) lwidth(thick)) ///
       (lowess observed_inc_ratio inc_rate_i if i_black_pct > 20 & i_black_pct <= 40, lcolor(orange) lwidth(thick)) ///
       (lowess observed_inc_ratio inc_rate_i if i_black_pct > 40 & i_black_pct <= 60, lcolor(red) lwidth(thick)) ///
       (lowess observed_inc_ratio inc_rate_i if i_black_pct > 60 & i_black_pct <= 80, lcolor(blue) lwidth(thick)) ///
       (lowess observed_inc_ratio inc_rate_i if i_black_pct > 80, lcolor(magenta) lwidth(thick)), ///
       title("Effect of Group i's Incarceration Rate, by i's categorization, on Disparity") ///
       ytitle("Observed Black:White Incarceration Ratio") ///
       xtitle("Incarceration Rate of Group i") ///
       legend(order(1 "< 20% Black" 2 "20-40% Black" 3 "40-60% Black" 4 "60-80% Black" 5 "> 80% Black")) ///
       yline(5, lpattern(dash) lcolor(black)) ///
       name(disparity_by_black_pct3, replace)
	   
gen i_size_pct_sq = i_size_pct^2
gen i_black_pct_sq = i_black_pct^2
gen inc_rate_i_sq = inc_rate_i^2

// Run regression to analyze factors affecting observed racial disparity, including the new parameter
regress observed_inc_ratio i_size_pct inc_rate_i i_black_pct c.i_size_pct#c.inc_rate_i c.i_size_pct#c.i_black_pct c.i_black_pct#c.inc_rate_i i_size_pct_sq i_black_pct_sq

*regress observed_inc_ratio i_size_pct inc_rate_i i_black_pct c.i_size_pct#c.inc_rate_i c.i_size_pct#c.i_black_pct c.i_black_pct#c.inc_rate_i i_size_pct_sq i_black_pct_sq inc_rate_i_sq


// Create a heatmap to show how the bias changes with group i size and % Black categorization
*gen i_size_pct_round = round(i_size_pct, 5)  // Round to nearest 5% for better visualization
*gen i_black_pct_round = round(i_black_pct, 10) // Round to nearest 10% for better visualization

// Create heatmap of bias by size and Black categorization
*twoway (contour ratio_bias_pct i_size_pct_round i_black_pct_round, ccuts(-30(5)30) ///
        ccolors(blue*1.4 blue*1.2 blue bluish cyan cyan*0.8 green_cyan green*0.8 green yellow orange red maroon) interp(none)), ///
       title("Heatmap: Bias in Racial Disparity Ratio (%)") ///
       xtitle("Group i Size (% of population)") ///
       ytitle("% of Group i Categorized as Black") ///
       xlabel(0(5)50) ylabel(0(10)100) ///
       name(heatmap_bias_by_black_pct, replace)

// Tabulate average bias by group i size and categorization
*table i_black_cat i_size_cat, statistic(mean ratio_bias_pct) nformat(%5.1f)



clear all
set seed 12345

**** SIMULATION PROGRAM WITH DIFFERENTIAL INCARCERATION BY CATEGORIZATION ****
capture program drop incarceration_sim_diff
program define incarceration_sim_diff, rclass
    // Input parameters
    args i_size        /* Size of group i (inconsistently categorized) */ ///
         inc_rate_i_white  /* Incarceration rate for group i categorized as White */ ///
         inc_rate_i_black  /* Incarceration rate for group i categorized as Black */ ///
         i_black_pct   /* Percentage of group i categorized as Black (0-100) */
         
    // Convert percentage to proportion
    local i_black_prop = `i_black_pct' / 100
    
    // Fixed incarceration rates for stable groups
    local inc_rate_w = 0.001  // 100 for stable White population
    local inc_rate_b = 0.005  // 500 for stable Black population
    
    // Preserve current dataset
    preserve
    
    // Setup population numbers (maintain 5:1 white:black ratio excluding group i)
    local b_ratio = 1
    local w_ratio = 5
    local ratio_total = `b_ratio' + `w_ratio'
    
    local remain_pop = 10000 - `i_size'
    local b_stable = round(`remain_pop' * (`b_ratio'/`ratio_total'))
    local w_stable = round(`remain_pop' * (`w_ratio'/`ratio_total'))
    
    // Double-check and adjust if needed
    if `b_stable' + `w_stable' != `remain_pop' {
        local w_stable = `remain_pop' - `b_stable'
    }
    
    // Create dataset with individual records
    clear
    set obs 10000
    
    // Assign true group membership (0=white stable, 1=black stable, 2=group i)
    gen true_group = 0 if _n <= `w_stable'
    replace true_group = 1 if _n > `w_stable' & _n <= (`w_stable' + `b_stable')
    replace true_group = 2 if _n > (`w_stable' + `b_stable')
    
// Assign observed race (0=white, 1=black)
gen black = (true_group == 1)  // All true blacks are observed as black
replace black = 0 if true_group == 0  // All true whites are observed as white

// For group i, assign racial categorization based on probability
gen random_draw = runiform() if true_group == 2
replace black = (random_draw <= `i_black_prop') if true_group == 2

// Create white indicator variable
gen white = 1 - black

// Create incarceration status variable - ONLY DEFINE THIS ONCE
gen incarcerated = 0  // Initialize with zeros
replace incarcerated = `inc_rate_w' if true_group == 0  // Exact rate for white stable
replace incarcerated = `inc_rate_b' if true_group == 1  // Exact rate for black stable
// Apply different incarceration rates based on categorization for group i
replace incarcerated = `inc_rate_i_white' if true_group == 2 & black == 0
replace incarcerated = `inc_rate_i_black' if true_group == 2 & black == 1


    
    // Calculate overall incarceration rate for group i (weighted average)
    quietly summarize incarcerated if true_group == 2
    local group_i_inc_rate = r(mean)
    
    // Calculate incarceration rates by observed categorization in group i only
    gen is_group_i = (true_group == 2)
    gen i_black_inc = black * incarcerated * is_group_i
    gen i_black = black * is_group_i
    quietly sum i_black_inc
    local i_black_inc_sum = r(sum)
    quietly sum i_black
    local i_black_sum = r(sum)
    local group_i_black_inc_rate = `i_black_inc_sum' / `i_black_sum'
    
    gen i_white_inc = white * incarcerated * is_group_i
    gen i_white = white * is_group_i
    quietly sum i_white_inc
    local i_white_inc_sum = r(sum)
    quietly sum i_white
    local i_white_sum = r(sum)
    local group_i_white_inc_rate = `i_white_inc_sum' / `i_white_sum'
    
    // Calculate true incarceration rates by real group
    quietly summarize incarcerated if true_group == 0
    local white_true_inc_rate = r(mean)
    
    quietly summarize incarcerated if true_group == 1
    local black_true_inc_rate = r(mean)
    
    // Calculate observed incarceration rates by observed race
    // For fractional outcomes, this requires weighted calculations
    
    // For observed black group
    gen black_inc_product = black * incarcerated  // For each person: P(black) * P(incarcerated)
    quietly sum black_inc_product
    local black_inc_total = r(sum)
    quietly sum black
    local black_total = r(sum)
    local observed_black_inc_rate = `black_inc_total' / `black_total'
    
    // For observed white group
    gen white_inc_product = white * incarcerated  // For each person: P(white) * P(incarcerated)
    quietly sum white_inc_product
    local white_inc_total = r(sum)
    quietly sum white
    local white_total = r(sum)
    local observed_white_inc_rate = `white_inc_total' / `white_total'
    
    // Calculate observed racial disparity
    local observed_inc_ratio = `observed_black_inc_rate'/`observed_white_inc_rate'
    
    // Calculate true racial disparity (excluding group i)
    local true_inc_ratio = `black_true_inc_rate'/`white_true_inc_rate'
    
    // Calculate bias due to inconsistent categorization
    local ratio_bias = `observed_inc_ratio' - `true_inc_ratio'
    local ratio_bias_pct = 100*(`observed_inc_ratio' - `true_inc_ratio')/`true_inc_ratio'
    
    // Calculate proportion of each observed group - using fractional values
    quietly sum black
    local observed_black_n = r(sum)
    quietly sum white
    local observed_white_n = r(sum)
    
    // Calculate what percent of each observed racial category is from group i
    gen black_group_i = black * is_group_i
    quietly sum black_group_i
    local black_from_i = r(sum)
    local i_in_black_pct = 100 * `black_from_i' / `observed_black_n'
    
    gen white_group_i = white * is_group_i
    quietly sum white_group_i
    local white_from_i = r(sum)
    local i_in_white_pct = 100 * `white_from_i' / `observed_white_n'
    
    // Return results
    return scalar true_inc_ratio = `true_inc_ratio'
    return scalar observed_inc_ratio = `observed_inc_ratio'
    return scalar ratio_bias = `ratio_bias'
    return scalar ratio_bias_pct = `ratio_bias_pct'
    
    return scalar white_true_inc_rate = `white_true_inc_rate'
    return scalar black_true_inc_rate = `black_true_inc_rate'
    return scalar group_i_inc_rate = `group_i_inc_rate'
    return scalar group_i_black_inc_rate = `group_i_black_inc_rate'
    return scalar group_i_white_inc_rate = `group_i_white_inc_rate'
    return scalar inc_rate_i_white = `inc_rate_i_white'
    return scalar inc_rate_i_black = `inc_rate_i_black'
    
    return scalar observed_black_inc_rate = `observed_black_inc_rate'
    return scalar observed_white_inc_rate = `observed_white_inc_rate'
    
    return scalar i_size = `i_size'
    return scalar i_size_pct = 100*`i_size'/10000
    return scalar i_black_pct = `i_black_pct'
    return scalar i_in_black_pct = `i_in_black_pct'
    return scalar i_in_white_pct = `i_in_white_pct'
    
    return scalar observed_black_pct = 100*`observed_black_n'/10000
    return scalar observed_white_pct = 100*`observed_white_n'/10000
    
    // Restore original dataset
    restore
end

**** RUNNING SIMULATIONS USING POSTFILE ****

// Set up output file
tempfile sim_results
postfile sim_handle i_size i_size_pct i_black_pct ///
                   inc_rate_i_white inc_rate_i_black ///
                   group_i_inc_rate group_i_black_inc_rate group_i_white_inc_rate ///
                   true_inc_ratio observed_inc_ratio ratio_bias ratio_bias_pct ///
                   white_true_inc_rate black_true_inc_rate ///
                   observed_black_inc_rate observed_white_inc_rate ///
                   i_in_black_pct i_in_white_pct ///
                   observed_black_pct observed_white_pct ///
                   using "`sim_results'", replace

// Run 10,000 simulations with random parameters
forvalues i = 1/10000 {
    // Generate random parameter values within realistic ranges
    local i_size = round(runiform(0, 5000))      // Size of group i (0-50% of population)
    
    // Generate White incarceration rate
    local inc_i_white = runiform(0.0005, 0.009999)    // Slightly reduced upper limit to allow room for Black rate
    
    // Generate Black incarceration rate and ensure it's higher than White rate
    local inc_i_black = `inc_i_white'
    // Keep generating a new rate until we get one higher than the White rate
    while `inc_i_black' <= `inc_i_white' {
        local inc_i_black = runiform(0.0005, 0.01)
    }
    
    local i_black_pct = runiform(0, 100)         // Random % of group i categorized as Black (0-100%) 
    
    // Run simulation with these parameters
    qui incarceration_sim_diff `i_size' `inc_i_white' `inc_i_black' `i_black_pct'
    
    // Store results
    post sim_handle (r(i_size)) (r(i_size_pct)) (r(i_black_pct)) ///
                   (r(inc_rate_i_white)) (r(inc_rate_i_black)) ///
                   (r(group_i_inc_rate)) (r(group_i_black_inc_rate)) (r(group_i_white_inc_rate)) ///
                   (r(true_inc_ratio)) (r(observed_inc_ratio)) ///
                   (r(ratio_bias)) (r(ratio_bias_pct)) ///
                   (r(white_true_inc_rate)) (r(black_true_inc_rate)) ///
                   (r(observed_black_inc_rate)) (r(observed_white_inc_rate)) ///
                   (r(i_in_black_pct)) (r(i_in_white_pct)) ///
                   (r(observed_black_pct)) (r(observed_white_pct))
}

// Close postfile and load results
postclose sim_handle
use "`sim_results'", clear

// Format variables for easier display
format inc_rate_i_white inc_rate_i_black group_i_inc_rate group_i_black_inc_rate group_i_white_inc_rate %5.3f
format observed_inc_ratio true_inc_ratio ratio_bias %4.2f
format ratio_bias_pct i_in_black_pct i_in_white_pct observed_black_pct observed_white_pct i_black_pct %4.1f

// Display summary statistics
summarize

// Verify that expected rates match actual rates
gen white_rate_diff = inc_rate_i_white - group_i_white_inc_rate
gen black_rate_diff = inc_rate_i_black - group_i_black_inc_rate
summarize white_rate_diff black_rate_diff, detail  // Should be near zero

summarize inc_rate_i_white, detail 
summarize inc_rate_i_black, detail
summarize group_i_white_inc_rate, detail
summarize group_i_black_inc_rate, detail



// Create incarceration rate gap variable
gen inc_rate_gap = inc_rate_i_black - inc_rate_i_white
summarize inc_rate_gap, detail

// Basic histograms of observed ratios
*histogram observed_inc_ratio, bin(30) color(blue%50) normal ///
    title("Distribution of Observed Black/White Incarceration Ratios") ///
    xtitle("Black/White Incarceration Ratio") ///
    name(hist_observed, replace)

// Explore relationship between group i size and observed disparity
twoway (scatter observed_inc_ratio i_size_pct) (lowess observed_inc_ratio i_size_pct), ///
    title("Effect of Inconsistently Categorized Group Size on Racial Disparity") ///
    xtitle("Group i as % of Population") ///
    ytitle("Observed Black/White Incarceration Ratio") ///
    name(scatter_size, replace) ///
    legend(off)

// Look at how the observed racial disparity changes with group i's incarceration rate gap
twoway (scatter observed_inc_ratio inc_rate_gap) (lowess observed_inc_ratio inc_rate_gap), ///
    title("Effect of Group i's Incarceration Rate Gap on Racial Disparity") ///
    xtitle("Incarceration Rate Gap (Black-White) in Group i") ///
    ytitle("Observed Black/White Incarceration Ratio") ///
    name(scatter_inc, replace) ///
    legend(off)

// New plot: Effect of % of group i categorized as Black on racial disparity
twoway (scatter observed_inc_ratio i_black_pct) (lowess observed_inc_ratio i_black_pct), ///
    title("Effect of Group i's Black Categorization on Racial Disparity") ///
    xtitle("% of Group i Categorized as Black") ///
    ytitle("Observed Black/White Incarceration Ratio") ///
    name(scatter_black_pct, replace) ///
    legend(off)

// Generate categories for group i size
*gen i_size_cat = "None" if i_size_pct == 0
*replace i_size_cat = "Small (1-10%)" if i_size_pct > 0 & i_size_pct <= 10
*replace i_size_cat = "Medium (10-25%)" if i_size_pct > 10 & i_size_pct <= 25
*replace i_size_cat = "Large (25-50%)" if i_size_pct > 25 & i_size_pct <= 50

// Generate categories for group i Black categorization
*gen i_black_cat = "Mostly White (0-25%)" if i_black_pct <= 25
*replace i_black_cat = "Mixed (25-75%)" if i_black_pct > 25 & i_black_pct < 75
*replace i_black_cat = "Mostly Black (75-100%)" if i_black_pct >= 75

// Generate rate gap categories
gen rate_gap_cat = "Small (<200)" if inc_rate_gap < 0.002
replace rate_gap_cat = "Medium (200-400)" if inc_rate_gap >= 0.002 & inc_rate_gap < 0.004
replace rate_gap_cat = "Large (400-600)" if inc_rate_gap >= .004 & inc_rate_gap < 0.006
replace rate_gap_cat = "Very Large (≥600)" if inc_rate_gap >= 0.006

// Look at how the observed racial disparity changes by size
// for different rate gaps
twoway (scatter observed_inc_ratio i_size_pct if rate_gap_cat=="Small (<200)", msize(small) mcolor(green%20)) ///
       (scatter observed_inc_ratio i_size_pct if rate_gap_cat=="Medium (200-400)", msize(small) mcolor(orange%20)) ///
       (scatter observed_inc_ratio i_size_pct if rate_gap_cat=="Large (400-600)", msize(small) mcolor(red%20)) ///
       (scatter observed_inc_ratio i_size_pct if rate_gap_cat=="Very Large (≥600)", msize(small) mcolor(blue%20)) ///
       (lowess observed_inc_ratio i_size_pct if rate_gap_cat=="Small (<200)", lcolor(green) lwidth(thick)) ///
       (lowess observed_inc_ratio i_size_pct if rate_gap_cat=="Medium (200-400)", lcolor(orange) lwidth(thick)) ///
       (lowess observed_inc_ratio i_size_pct if rate_gap_cat=="Large (400-600)", lcolor(red) lwidth(thick)) ///
       (lowess observed_inc_ratio i_size_pct if rate_gap_cat== "Very Large (≥600)", lcolor(blue) lwidth(thick)), ///
       title("Effect of Group i Size by Incarceration Rate Gap") ///
       ytitle("Observed Black:White Incarceration Ratio") ///
       xtitle("Group i as % of Population") ///
       legend(order(5 "Rate Gap <200" 6 "Rate Gap 200-400" 7 "Rate Gap 400-600" 8 "Rate Gap ≥600")) ///
       yline(5, lpattern(dash) lcolor(black)) ///
       name(disparity_by_size_gap, replace)

// Look at how racial categorization affects disparity by rate gap
*twoway (scatter observed_inc_ratio i_black_pct if rate_gap_cat=="Small (<200)", msize(small) mcolor(green%20)) ///
       (scatter observed_inc_ratio i_black_pct if rate_gap_cat=="Medium (200-400)", msize(small) mcolor(orange%20)) ///
       (scatter observed_inc_ratio i_black_pct if rate_gap_cat=="Large (400-600)", msize(small) mcolor(red%20)) ///
       (scatter observed_inc_ratio i_black_pct if rate_gap_cat=="Very Large (≥600)", msize(small) mcolor(blue%20)) ///
       (lowess observed_inc_ratio i_black_pct if rate_gap_cat=="Small (<200)", lcolor(green) lwidth(thick)) ///
       (lowess observed_inc_ratio i_black_pct if rate_gap_cat=="Medium (200-400)", lcolor(orange) lwidth(thick)) ///
       (lowess observed_inc_ratio i_black_pct if rate_gap_cat=="Large (400-600)", lcolor(red) lwidth(thick)) ///
       (lowess observed_inc_ratio i_black_pct if rate_gap_cat=="Very Large (≥600)", lcolor(blue) lwidth(thick)), ///
       title("Effect of Group i's Categorization by Incarceration Rate Gap") ///
       ytitle("Observed Black:White Incarceration Ratio") ///
       xtitle("% of Group i Categorized as Black") ///
       legend(order(5 "Rate Gap <200" 6 "Rate Gap 200-400" 7 "Rate Gap 400-600" 8 "Rate Gap ≥600")) ///
       yline(5, lpattern(dash) lcolor(black)) ///
       name(disparity_by_black_pct_gap, replace)

// Look at how rate gap affects disparity by % black categorization
twoway (scatter observed_inc_ratio inc_rate_gap if i_black_pct <= 20, msize(small) mcolor(green%15)) ///
       (scatter observed_inc_ratio inc_rate_gap if i_black_pct > 20 & i_black_pct <= 40, msize(small) mcolor(orange%15)) ///
       (scatter observed_inc_ratio inc_rate_gap if i_black_pct > 40 & i_black_pct <= 60, msize(small) mcolor(red%15)) ///
       (scatter observed_inc_ratio inc_rate_gap if i_black_pct > 60 & i_black_pct <= 80, msize(small) mcolor(blue%15)) ///
       (scatter observed_inc_ratio inc_rate_gap if i_black_pct > 80, msize(small) mcolor(purple%15)) ///
       (lowess observed_inc_ratio inc_rate_gap if i_black_pct <= 20, lcolor(green) lwidth(thick)) ///
       (lowess observed_inc_ratio inc_rate_gap if i_black_pct > 20 & i_black_pct <= 40, lcolor(orange) lwidth(thick)) ///
       (lowess observed_inc_ratio inc_rate_gap if i_black_pct > 40 & i_black_pct <= 60, lcolor(red) lwidth(thick)) ///
       (lowess observed_inc_ratio inc_rate_gap if i_black_pct > 60 & i_black_pct <= 80, lcolor(blue) lwidth(thick)) ///
       (lowess observed_inc_ratio inc_rate_gap if i_black_pct > 80, lcolor(magenta) lwidth(thick)), ///
       title("Effect of Rate Gap by Group i's Categorization on Disparity") ///
       ytitle("Observed Black:White Incarceration Ratio") ///
       xtitle("Incarceration Rate Gap (Black-White)") ///
       legend(order(1 "< 20% Black" 2 "20-40% Black" 3 "40-60% Black" 4 "60-80% Black" 5 "> 80% Black")) ///
       yline(5, lpattern(dash) lcolor(black)) ///
       name(disparity_by_gap_cat, replace)

gen i_size_pct_sq = i_size_pct^2

// Run regression to analyze factors affecting observed racial disparity, including the new parameter
regress observed_inc_ratio i_size_pct inc_rate_i_white inc_rate_i_black i_black_pct ///
                         c.i_size_pct#c.inc_rate_gap c.i_size_pct#c.i_black_pct i_size_pct_sq /// 
						 



// Tabulate average bias by group i size and categorization (Stata 17+ compatible)
*table i_black_cat i_size_cat, statistic(mean ratio_bias_pct) nformat(%5.1f)

// Tabulate average bias by rate gap and categorization (Stata 17+ compatible)
*table rate_gap_cat i_black_cat, statistic(mean ratio_bias_pct) nformat(%5.1f)
