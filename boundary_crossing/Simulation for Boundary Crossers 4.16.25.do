**** SIMULATION PROGRAM ONE: WIDE RANGE OF MOVERS' INCARCRATION RATES****

clear all
set seed 12345


capture program drop incarceration_sim
program define incarceration_sim, rclass
    // Input parameters
    args movers    /* Number of people moving in each direction */ ///
         inc_rate_b2w    /* Incarceration rate - Black to White movers */ ///
         inc_rate_w2b    /* Incarceration rate - White to Black movers */
         
    // Fixed incarceration rates for remainers
    local inc_rate_w = 0.001  // 100/100,000 for White remainers
    local inc_rate_b = 0.005  // 500/100,000 for Black remainers
    
    // Preserve current dataset
    preserve
    
    // Setup population numbers (total population = 10,000)
    local total_pop = 10000
    local b_pop = 1500        // Fixed Black population (15%)
    local w_pop = 8500        // Fixed White population (85%)
    
    // Calculate movement frequencies (for reporting purposes)
    local move_freq_b2w = `movers' / `b_pop'
    local move_freq_w2b = `movers' / `w_pop'
    
    // Create dataset with individual records
    clear
    set obs `total_pop'
    
    // Initial race assignment (1=Black, 0=White)
    gen black = (_n <= `b_pop')
    
    // Assign movers (individuals who change categories)
    gen mover = 0
    replace mover = 1 if black==1 & _n <= `movers'                    // Black to White movers
    replace mover = 2 if black==0 & _n > (10000 - `movers')              // Last movers White people
    
    // Post-movement race
    gen new_black = black
    replace new_black = 0 if mover==1    // Black to White
    replace new_black = 1 if mover==2    // White to Black
    
    // Assign expected incarceration probabilities based on movement pattern
    // This replaces the binary incarcerated variable with a probability value
    gen exp_incarceration = 0
    
    // Non-movers get their group's standard rate
    replace exp_incarceration = `inc_rate_b' if black==1 & mover==0    // Black remainers
    replace exp_incarceration = `inc_rate_w' if black==0 & mover==0    // White remainers
    
    // Movers get their specific rates from parameters
    replace exp_incarceration = `inc_rate_b2w' if mover==1    // Black to White movers
    replace exp_incarceration = `inc_rate_w2b' if mover==2    // White to Black movers
    
    // ================ PRE-MOVEMENT ANALYSIS ================
    // Calculate mean incarceration rates by ORIGINAL racial category (pre-movement)
    quietly summarize exp_incarceration if black==1
    local pre_black_inc_rate = r(mean)
    
    quietly summarize exp_incarceration if black==0
    local pre_white_inc_rate = r(mean)
    
    // Calculate incarceration rate ratio using original categories
    local pre_inc_ratio = `pre_black_inc_rate'/`pre_white_inc_rate'
    
    // ================ POST-MOVEMENT ANALYSIS ================
    // Calculate observed incarceration rates by POST-movement race
    quietly summarize exp_incarceration if new_black==1
    local post_black_inc_rate = r(mean)
    
    quietly summarize exp_incarceration if new_black==0
    local post_white_inc_rate = r(mean)
    
    // Calculate incarceration rate ratio after movement
    local post_inc_ratio = `post_black_inc_rate'/`post_white_inc_rate'
    
    // Calculate ratio change due to mobility
    local ratio_change = `post_inc_ratio' - `pre_inc_ratio'
    local ratio_change_pct = 100*(`post_inc_ratio' - `pre_inc_ratio')/`pre_inc_ratio'
    
    // Calculate proportion of each group post-movement
    qui count if new_black==1
    local final_black_n = r(N)
    qui count if new_black==0
    local final_white_n = r(N)
    
    // Calculate incarceration rates for each mobility pattern
    qui summarize exp_incarceration if black==1 & mover==0
    local black_remain_rate = r(mean)
    qui summarize exp_incarceration if black==0 & mover==0
    local white_remain_rate = r(mean)
    qui summarize exp_incarceration if mover==1
    local black_to_white_rate = r(mean)
    qui summarize exp_incarceration if mover==2
    local white_to_black_rate = r(mean)
    
    // Return results - both pre and post movement
    return scalar pre_inc_ratio = `pre_inc_ratio'
    return scalar post_inc_ratio = `post_inc_ratio'
    return scalar ratio_change = `ratio_change'
    return scalar ratio_change_pct = `ratio_change_pct'
    
    return scalar pre_black_inc_rate = `pre_black_inc_rate'
    return scalar pre_white_inc_rate = `pre_white_inc_rate'
    return scalar post_black_inc_rate = `post_black_inc_rate'
    return scalar post_white_inc_rate = `post_white_inc_rate'
    
    return scalar black_remain_rate = `black_remain_rate'
    return scalar white_remain_rate = `white_remain_rate'
    return scalar black_to_white_rate = `black_to_white_rate'
    return scalar white_to_black_rate = `white_to_black_rate'
    
    return scalar black_pct = `final_black_n'/`total_pop'
    return scalar white_pct = `final_white_n'/`total_pop'
    return scalar b_pop_original = `b_pop'
    return scalar w_pop_original = `w_pop'
    return scalar movers = `movers'
    return scalar move_freq_b2w = `move_freq_b2w'
    return scalar move_freq_w2b = `move_freq_w2b'
    
    // Restore original dataset
    restore
end

**** RUNNING SIMULATIONS USING POSTFILE ****

// Set up output file
tempfile sim_results
postfile sim_handle movers move_freq_b2w move_freq_w2b inc_rate_b2w inc_rate_w2b ///
                   pre_inc_ratio post_inc_ratio ratio_change ratio_change_pct ///
                   pre_black_inc_rate pre_white_inc_rate ///
                   post_black_inc_rate post_white_inc_rate ///
                   black_remain_rate white_remain_rate ///
                   black_to_white_rate white_to_black_rate ///
                   black_pct white_pct ///
                   using "`sim_results'", replace

// Generate parameter combinations
forvalues i = 1/10000 {
    // Generate random parameter values
    local movers = round(runiform(0, 750))     // Number of movers (0-750 people in each direction)
    local irb2w = runiform(0.0005, 0.01)          // Incarceration rate for Black to White movers
    local irw2b = runiform(0.0005, 0.01)          // Incarceration rate for White to Black movers
    
    // Run simulation with these parameters
    qui incarceration_sim `movers' `irb2w' `irw2b'
    
    // Store results
    post sim_handle (r(movers)) (r(move_freq_b2w)) (r(move_freq_w2b)) (`irb2w') (`irw2b') ///
                   (r(pre_inc_ratio)) (r(post_inc_ratio)) (r(ratio_change)) (r(ratio_change_pct)) ///
                   (r(pre_black_inc_rate)) (r(pre_white_inc_rate)) ///
                   (r(post_black_inc_rate)) (r(post_white_inc_rate)) ///
                   (r(black_remain_rate)) (r(white_remain_rate)) ///
                   (r(black_to_white_rate)) (r(white_to_black_rate)) ///
                   (r(black_pct)) (r(white_pct))
}

// Close postfile and load results
postclose sim_handle
use "`sim_results'", clear

**** ANALYSIS OF RESULTS ****

// Basic summary of pre- and post-movement incarceration ratios
summarize pre_inc_ratio post_inc_ratio ratio_change ratio_change_pct, detail

// Histogram of pre- and post-movement incarceration rate ratios
*histogram pre_inc_ratio, color(blue%30) bin(20) ///
    addplot(histogram post_inc_ratio, color(red%30) bin(20)) ///
    legend(order(1 "Pre-Movement" 2 "Post-Movement")) ///
    title("Distribution of Black-White Incarceration Ratios") ///
    subtitle("Before and After Mobility") name(hist_compare, replace)

// Histogram of ratio changes
*histogram ratio_change, bin(20) color(green%50) normal ///
    title("Change in Incarceration Rate Ratio Due to Mobility") ///
    subtitle("Positive values = mobility increases disparity") ///
    name(hist_change, replace)

// Examine relationship between mobility level and ratio change
*scatter ratio_change movers, name(scatter_change1, replace) ///
    title("Effect of Mobility on Incarceration Ratio Change") ///
    xtitle("Number of People Moving in Each Direction") ///
    ytitle("Change in Black/White Incarceration Ratio")

// Add fitted line to see trend    
*twoway (scatter ratio_change movers) (lowess ratio_change movers), ///
    name(scatter_change2, replace) ///
    title("Effect of Mobility on Incarceration Ratio Change") ///
    xtitle("Number of People Moving in Each Direction") ///
    ytitle("Change in Black/White Incarceration Ratio") ///
    legend(off)
    
// Effect of incarceration rates of movers on ratio change
*twoway (scatter ratio_change inc_rate_b2w) (lowess ratio_change inc_rate_b2w), ///
    name(graph_change1, replace) ///
    title("Effect of Black→White Movers' Inc. Rate on Ratio Change") ///
    xtitle("Black→White Movers' Incarceration Rate") ///
    ytitle("Change in Incarceration Ratio") legend(off)


	 

// Create interesting comparisons: mobility effect by mover incarceration profile
gen mover_profile = .
replace mover_profile = 1 if inc_rate_b2w <= .00125 & inc_rate_b2w >=.00075 & inc_rate_w2b >= .00375 & inc_rate_w2b <= .00625  // Like Destination Category
replace mover_profile = 2 if inc_rate_b2w >= .00375 & inc_rate_b2w <= .00625  & inc_rate_w2b <=.00125 & inc_rate_w2b >=.00075 // Like Origin Category


label define prof_lab 0 "Other" 1 "Like Destination Category" 2 "Like Origin Category" 
label values mover_profile prof_lab

// Effect of mobility by mover profile
bysort mover_profile: sum post_inc_ratio
bysort mover_profile: sum pre_inc_ratio

// Create high mobility indicator variable
gen high_mobility = (movers >= 375)
label define mob_lab 0 "Lower Mobility" 1 "Higher Mobility"
label values high_mobility mob_lab

// Now use the table command with the new variable
table mover_profile high_mobility, statistic(mean pre_inc_ratio) statistic (mean post_inc_ratio) statistic(count ratio_change)


// Display a compact summary of pre/post values by mobility level
*gen mobility_level = "Low" if movers < 250
*replace mobility_level = "Medium" if movers >= 250 & movers < 500
*replace mobility_level = "High" if movers >= 500

*label var pre_inc_ratio "Ratio Before Movement"
*label var post_inc_ratio "Ratio After Movement"
*label var ratio_change "Change in Ratio"
*label var ratio_change_pct "Percent Change"

*table mobility_level, statistic(mean pre_inc_ratio) statistic(mean post_inc_ratio) ///
                    statistic(mean ratio_change) statistic(mean ratio_change_pct) ///
                    statistic(count ratio_change)


// Verify 5:1 ratio is maintained for remainers
sum black_remain_rate white_remain_rate
gen remain_rate_ratio = black_remain_rate/white_remain_rate
summarize remain_rate_ratio




// Histogram of incarceration ratios 
*histogram post_inc_ratio, bin(20) normal title("Distribution of Black-White Incarceration Ratios") ///
    subtitle("Equal numbers moving each way, Inc. rates 5%/1%") name(post_inc_ratio, replace)



// Effect of incarceration rates of movers
*Add prediction intervals) 
twoway (scatter post_inc_ratio inc_rate_b2w) (lowess post_inc_ratio inc_rate_b2w), ///
    name(post_rate_by_b2w1, replace) title("Post-Movement Disparity, by Black-to-White Movers' Incarceration Rate") ///
    xtitle("Black-to-White Movers' Incarceration Rate") ///
    ytitle("Black/White Incarceration Ratio") legend(off)


twoway (scatter post_inc_ratio inc_rate_w2b) (lowess post_inc_ratio inc_rate_w2b), ///
    name(post_rate_by_w2b1, replace) title("Post-Movement Disparity, by White-to-Black Movers' Incarceration Rate") ///
    xtitle("White-to-Black Movers' Incarceration Rate") ///
    ytitle("Black/White Incarceration Ratio") legend(off)
	

twoway (scatter ratio_change inc_rate_b2w) (lowess ratio_change inc_rate_b2w), ///
    name(change_by_b2w1, replace) title("Change in Disparity, by Black-to-White Movers' Incarceration Rate") ///
    xtitle("Black-to-White Movers' Incarceration Rate") ///
    ytitle("Change in Black/White Disparity") legend(off)

twoway (scatter ratio_change inc_rate_w2b) (lowess ratio_change inc_rate_w2b), ///
    name(change_by_w2b1, replace) title("Change in Disparity, by White-to-Black Movers' Incarceration Rate") ///
    xtitle("White-to-Black Movers' Incarceration Rate") ///
    ytitle("Change in Black/White Disparity") legend(off)

// Regression analysis of factors affecting the incarceration rate ratio
regress post_inc_ratio movers inc_rate_b2w inc_rate_w2b c.movers#c.inc_rate_w2b c.movers#c.inc_rate_b2w



*Graph with Prediction intervals: Post-Incarceration Rate 
	 

// Sort by x-variable
sort  move_freq_b2w

// Run quantile regressions with polynomial terms
gen  move_freq_b2w_sq =  move_freq_b2w^2

// Median (50th percentile)
qreg post_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.5)
predict median_poly_post 

// Lower bound (2.5th percentile)
qreg post_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.025)
predict lower_poly_post 

// Upper bound (97.5th percentile)
qreg post_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.975)
predict upper_poly_post 

// Graph the results
twoway (scatter post_inc_ratio move_freq_b2w, mcolor(navy%40)) ///
       (line median_poly_post  move_freq_b2w, sort lcolor(red) lwidth(medthick)) ///
       (rarea lower_poly_post upper_poly_post move_freq_b2w, sort color(red%15)), ///
       title("Post-Movement Black-White Incarceration by Movers") ///
       subtitle("With nonlinear quantile regression prediction bands") ///
       xtitle("Movers, as Share of Black Population") ///
       ytitle("Black/White Incarceration Ratio") ///
       legend(order(1 "Observed Ratios" 2 "Median Fit" 3 "95% Prediction Band")) ///
       name(Disparity_by_Movers1, replace)
	  
*Graph with Prediction Intervals: Pre-Incarceration Rates 



// Median (50th percentile)
qreg pre_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.5)
predict median_poly_pre

// Lower bound (2.5th percentile)
qreg pre_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.025)
predict lower_poly_pre

// Upper bound (97.5th percentile)
qreg pre_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.975)
predict upper_poly_pre 

// Graph the results
twoway (scatter pre_inc_ratio move_freq_b2w, mcolor(navy%40)) ///
       (line median_poly_pre move_freq_b2w, sort lcolor(red) lwidth(medthick)) ///
       (rarea lower_poly_pre upper_poly_pre  move_freq_b2w, sort color(red%15)), ///
       title("Pre-Movement Black-White Incarceration Stability") ///
       subtitle("With nonlinear quantile regression prediction bands") ///
       xtitle("Movers, as Share of Black Population") ///
       ytitle("Black/White Incarceration Ratio") ///
       legend(order(1 "Observed Ratios" 2 "Median Fit" 3 "95% Prediction Band")) ///
       name(Pre_by_Movers1, replace)

*Graph with Prediction Intervals: Change in Incarceration Rates 


// Median (50th percentile)
qreg ratio_change  move_freq_b2w move_freq_b2w_sq, q(.5)
predict median_poly_change

// Lower bound (2.5th percentile)
qreg ratio_change move_freq_b2w move_freq_b2w_sq, q(.025)
predict lower_poly_change

// Upper bound (97.5th percentile)
qreg ratio_change move_freq_b2w move_freq_b2w_sq, q(.975)
predict upper_poly_change

// Graph the results
twoway (scatter ratio_change move_freq_b2w, mcolor(navy%40)) ///
       (line median_poly_change move_freq_b2w, sort lcolor(red) lwidth(medthick)) ///
       (rarea lower_poly_change upper_poly_change move_freq_b2w, sort color(red%15)), ///
       title("Change in Disparity") ///
       subtitle("With nonlinear quantile regression prediction bands") ///
       xtitle("Movers, as Share of Black Population") ///
       ytitle("Change in Black/White Incarceration Ratio") ///
       legend(order(1 "Observed Ratios" 2 "Median Fit" 3 "95% Prediction Band")) ///
       name(Change_byMovers1, replace)

	   
	   
	   
****** SECOND SIMULATION: Restricted Range of Movers' Incarceration Rates

clear all
set seed 12345

**** SIMULATION PROGRAM ****
capture program drop incarceration_sim
program define incarceration_sim, rclass
    // Input parameters
    args movers    /* Number of people moving in each direction */ ///
         inc_rate_b2w    /* Incarceration rate - Black to White movers */ ///
         inc_rate_w2b    /* Incarceration rate - White to Black movers */
         
    // Fixed incarceration rates for remainers
    local inc_rate_w = 0.001  // 100/100,000 for White remainers
    local inc_rate_b = 0.005  // 500/100,000 for Black remainers
    
    // Preserve current dataset
    preserve
    
    // Setup population numbers (total population = 10,000)
    local total_pop = 10000
    local b_pop = 1500        // Fixed Black population (15%)
    local w_pop = 8500        // Fixed White population (85%)
    
    // Calculate movement frequencies (for reporting purposes)
    local move_freq_b2w = `movers' / `b_pop'
    local move_freq_w2b = `movers' / `w_pop'
    
    // Create dataset with individual records
    clear
    set obs `total_pop'
    
    // Initial race assignment (1=Black, 0=White)
    gen black = (_n <= `b_pop')
    
    // Assign movers (individuals who change categories)
    gen mover = 0
    replace mover = 1 if black==1 & _n <= `movers'                    // Black to White movers
    replace mover = 2 if black==0 & _n > (10000 - `movers')           // White to Black movers
    
    // Post-movement race
    gen new_black = black
    replace new_black = 0 if mover==1    // Black to White
    replace new_black = 1 if mover==2    // White to Black
    
    // Assign expected incarceration rates based on movement pattern
    gen exp_incarceration = 0
    
    // Non-movers get their group's standard rate
    replace exp_incarceration = `inc_rate_b' if black==1 & mover==0    // Black remainers
    replace exp_incarceration = `inc_rate_w' if black==0 & mover==0    // White remainers
    
    // Movers get their specific rates from parameters
    replace exp_incarceration = `inc_rate_b2w' if mover==1    // Black to White movers
    replace exp_incarceration = `inc_rate_w2b' if mover==2    // White to Black movers
    
    // ================ PRE-MOVEMENT ANALYSIS ================
    // Calculate incarceration rates by ORIGINAL racial category (pre-movement)
    quietly summarize exp_incarceration if black==1
    local pre_black_inc_rate = r(mean)
    
    quietly summarize exp_incarceration if black==0
    local pre_white_inc_rate = r(mean)
    
    // Calculate incarceration rate ratio using original categories
    local pre_inc_ratio = `pre_black_inc_rate'/`pre_white_inc_rate'
    
    // ================ POST-MOVEMENT ANALYSIS ================
    // Calculate observed incarceration rates by POST-movement race
    quietly summarize exp_incarceration if new_black==1
    local post_black_inc_rate = r(mean)
    
    quietly summarize exp_incarceration if new_black==0
    local post_white_inc_rate = r(mean)
    
    // Calculate incarceration rate ratio after movement
    local post_inc_ratio = `post_black_inc_rate'/`post_white_inc_rate'
    
    // Calculate ratio change due to mobility
    local ratio_change = `post_inc_ratio' - `pre_inc_ratio'
    local ratio_change_pct = 100*(`post_inc_ratio' - `pre_inc_ratio')/`pre_inc_ratio'
    
    // Calculate proportion of each group post-movement
    qui count if new_black==1
    local final_black_n = r(N)
    qui count if new_black==0
    local final_white_n = r(N)
    
    // Calculate incarceration rates for each mobility pattern
    qui summarize exp_incarceration if black==1 & mover==0
    local black_remain_rate = r(mean)
    qui summarize exp_incarceration if black==0 & mover==0
    local white_remain_rate = r(mean)
    qui summarize exp_incarceration if mover==1
    local black_to_white_rate = r(mean)
    qui summarize exp_incarceration if mover==2
    local white_to_black_rate = r(mean)
    
    // Return results - both pre and post movement
    return scalar pre_inc_ratio = `pre_inc_ratio'
    return scalar post_inc_ratio = `post_inc_ratio'
    return scalar ratio_change = `ratio_change'
    return scalar ratio_change_pct = `ratio_change_pct'
    
    return scalar pre_black_inc_rate = `pre_black_inc_rate'
    return scalar pre_white_inc_rate = `pre_white_inc_rate'
    return scalar post_black_inc_rate = `post_black_inc_rate'
    return scalar post_white_inc_rate = `post_white_inc_rate'
    
    return scalar black_remain_rate = `black_remain_rate'
    return scalar white_remain_rate = `white_remain_rate'
    return scalar black_to_white_rate = `black_to_white_rate'
    return scalar white_to_black_rate = `white_to_black_rate'
    
    return scalar black_pct = `final_black_n'/`total_pop'
    return scalar white_pct = `final_white_n'/`total_pop'
    return scalar b_pop_original = `b_pop'
    return scalar w_pop_original = `w_pop'
    return scalar movers = `movers'
    return scalar move_freq_b2w = `move_freq_b2w'
    return scalar move_freq_w2b = `move_freq_w2b'
    
    // Restore original dataset
    restore
end

**** RUNNING SIMULATIONS USING POSTFILE ****

// Set up output file
tempfile sim_results
postfile sim_handle movers move_freq_b2w move_freq_w2b inc_rate_b2w inc_rate_w2b ///
                   pre_inc_ratio post_inc_ratio ratio_change ratio_change_pct ///
                   pre_black_inc_rate pre_white_inc_rate ///
                   post_black_inc_rate post_white_inc_rate ///
                   black_remain_rate white_remain_rate ///
                   black_to_white_rate white_to_black_rate ///
                   black_pct white_pct ///
                   using "`sim_results'", replace

// Generate parameter combinations
forvalues i = 1/10000 {
    // Generate random parameter values
    local movers = round(runiform(0, 750))     // Number of movers (0-750 people in each direction)
    local irb2w = runiform(0.001, 0.005)       // Incarceration rate for Black to White movers
    local irw2b = runiform(0.001, 0.005)       // Incarceration rate for White to Black movers
    
    // Run simulation with these parameters
    qui incarceration_sim `movers' `irb2w' `irw2b'
    
    // Store results
    post sim_handle (r(movers)) (r(move_freq_b2w)) (r(move_freq_w2b)) (`irb2w') (`irw2b') ///
                   (r(pre_inc_ratio)) (r(post_inc_ratio)) (r(ratio_change)) (r(ratio_change_pct)) ///
                   (r(pre_black_inc_rate)) (r(pre_white_inc_rate)) ///
                   (r(post_black_inc_rate)) (r(post_white_inc_rate)) ///
                   (r(black_remain_rate)) (r(white_remain_rate)) ///
                   (r(black_to_white_rate)) (r(white_to_black_rate)) ///
                   (r(black_pct)) (r(white_pct))
}

// Close postfile and load results
postclose sim_handle
use "`sim_results'", clear

**** ANALYSIS OF RESULTS ****

// Basic summary of pre- and post-movement incarceration ratios
summarize pre_inc_ratio post_inc_ratio ratio_change ratio_change_pct, detail

// Histogram of pre- and post-movement incarceration rate ratios
histogram pre_inc_ratio, color(blue%30) bin(20) ///
    addplot(histogram post_inc_ratio, color(red%30) bin(20)) ///
    legend(order(1 "Pre-Movement" 2 "Post-Movement")) ///
    title("Distribution of Black-White Incarceration Ratios") ///
    subtitle("Before and After Mobility") name(hist_compare, replace)

// Histogram of ratio changes
histogram ratio_change, bin(20) color(green%50) normal ///
    title("Change in Incarceration Rate Ratio Due to Mobility") ///
    subtitle("Positive values = mobility increases disparity") ///
    name(hist_change, replace)

// Examine relationship between mobility level and ratio change
scatter ratio_change movers, name(scatter_change1, replace) ///
    title("Effect of Mobility on Incarceration Ratio Change") ///
    xtitle("Number of People Moving in Each Direction") ///
    ytitle("Change in Black/White Incarceration Ratio")

// Add fitted line to see trend    
*twoway (scatter ratio_change movers) (lowess ratio_change movers), ///
    name(scatter_change2, replace) ///
    title("Effect of Mobility on Incarceration Ratio Change") ///
    xtitle("Number of People Moving in Each Direction") ///
    ytitle("Change in Black/White Incarceration Ratio") ///
    legend(off)
    
// Effect of incarceration rates of movers on ratio change
*twoway (scatter ratio_change inc_rate_b2w) (lowess ratio_change inc_rate_b2w), ///
    name(graph_change1, replace) ///
    title("Effect of Black→White Movers' Inc. Rate on Ratio Change") ///
    xtitle("Black→White Movers' Incarceration Rate") ///
    ytitle("Change in Incarceration Ratio") legend(off)


	 

// Create interesting comparisons: mobility effect by mover incarceration profile
*gen mover_profile = .
*replace mover_profile = 1 if inc_rate_b2w <= .00125 & inc_rate_b2w >=.00075 & inc_rate_w2b >= .00375 & inc_rate_w2b <= .00625  // Like Destination Category
*replace mover_profile = 2 if inc_rate_b2w >= .00375 & inc_rate_b2w <= .00625  & inc_rate_w2b <=.00125 & inc_rate_w2b >=.00075 // Like Origin Category


*label define prof_lab 0 "Other" 1 "Like Destination Category" 2 "Like Origin Category" 
*label values mover_profile prof_lab

// Effect of mobility by mover profile
*bysort mover_profile: sum post_inc_ratio
*bysort mover_profile: sum pre_inc_ratio

// Create high mobility indicator variable
*gen high_mobility = (movers >= 375)
*label define mob_lab 0 "Lower Mobility" 1 "Higher Mobility"
*label values high_mobility mob_lab

// Now use the table command with the new variable
*table mover_profile high_mobility, statistic(mean pre_inc_ratio) statistic (mean post_inc_ratio) statistic(count ratio_change)


// Display a compact summary of pre/post values by mobility level
*gen mobility_level = "Low" if movers < 250
*replace mobility_level = "Medium" if movers >= 250 & movers < 500
*replace mobility_level = "High" if movers >= 500

*label var pre_inc_ratio "Ratio Before Movement"
*label var post_inc_ratio "Ratio After Movement"
*label var ratio_change "Change in Ratio"
*label var ratio_change_pct "Percent Change"

*table mobility_level, statistic(mean pre_inc_ratio) statistic(mean post_inc_ratio) ///
                    statistic(mean ratio_change) statistic(mean ratio_change_pct) ///
                    statistic(count ratio_change)


// Verify 5:1 ratio is maintained for remainers
sum black_remain_rate white_remain_rate
gen remain_rate_ratio = black_remain_rate/white_remain_rate
summarize remain_rate_ratio

// Basic summary of observed incarceration rate ratios
summarize post_inc_ratio, detail


// Histogram of incarceration ratios 
*histogram post_inc_ratio, bin(20) normal title("Distribution of Black-White Incarceration Ratios") ///
    subtitle("Equal numbers moving each way, Inc. rates 5%/1%") name(post_inc_ratio, replace)



// Effect of incarceration rates of movers
*Add prediction intervals) 
twoway (scatter post_inc_ratio inc_rate_b2w) (lowess post_inc_ratio inc_rate_b2w), ///
    name(post_by_b2w2, replace) title("Post-Movement Disparity, by Black-to-White Movers' Incarceration Rate") ///
    xtitle("Black-to-White Movers' Incarceration Rate") ///
    ytitle("Black/White Incarceration Ratio") legend(off)


twoway (scatter post_inc_ratio inc_rate_w2b) (lowess post_inc_ratio inc_rate_w2b), ///
    name(post_by_w2b2, replace) title("Post-Movement Disparity, by White-to-Black Movers' Incarceration Rate") ///
    xtitle("White-to-Black Movers' Incarceration Rate") ///
    ytitle("Black/White Incarceration Ratio") legend(off)
	

*twoway (scatter ratio_change inc_rate_b2w) (lowess ratio_change inc_rate_b2w), ///
    name(change_by_b2w2, replace) title("Change in Disparity, by Black-to-White Movers' Incarceration Rate") ///
    xtitle("Black-to-White Movers' Incarceration Rate") ///
    ytitle("Change in Black/White Disparity") legend(off)

*twoway (scatter ratio_change inc_rate_w2b) (lowess ratio_change inc_rate_w2b), ///
    name(change_by_w2b2, replace) title("Change in Disparity, by White-to-Black Movers' Incarceration Rate") ///
    xtitle("White-to-Black Movers' Incarceration Rate") ///
    ytitle("Change in Black/White Disparity") legend(off)

// Regression analysis of factors affecting the incarceration rate ratio
regress post_inc_ratio movers inc_rate_b2w inc_rate_w2b c.movers#c.inc_rate_w2b c.movers#c.inc_rate_b2w



*Graph with Prediction intervals: Post-Incarceration Rate 
	 

// Sort by x-variable
sort  move_freq_b2w

// Run quantile regressions with polynomial terms
gen  move_freq_b2w_sq =  move_freq_b2w^2

// Median (50th percentile)
qreg post_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.5)
predict median_poly_post 

// Lower bound (2.5th percentile)
qreg post_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.025)
predict lower_poly_post 

// Upper bound (97.5th percentile)
qreg post_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.975)
predict upper_poly_post 

// Graph the results
twoway (scatter post_inc_ratio move_freq_b2w, mcolor(navy%40)) ///
       (line median_poly_post  move_freq_b2w, sort lcolor(red) lwidth(medthick)) ///
       (rarea lower_poly_post upper_poly_post move_freq_b2w, sort color(red%15)), ///
       title("Post-Movement Black-White Incarceration, by Movers") ///
       subtitle("With nonlinear quantile regression prediction bands") ///
       xtitle("Movers, as Share of Black Population") ///
       ytitle("Black/White Incarceration Ratio") ///
       legend(order(1 "Observed Ratios" 2 "Median Fit" 3 "95% Prediction Band")) ///
       name(Disparity_by_Movers2, replace)
	  
*Graph with Prediction Intervals: Pre-Incarceration Rates 



// Median (50th percentile)
qreg pre_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.5)
predict median_poly_pre

// Lower bound (2.5th percentile)
qreg pre_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.025)
predict lower_poly_pre

// Upper bound (97.5th percentile)
qreg pre_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.975)
predict upper_poly_pre 

// Graph the results
*twoway (scatter pre_inc_ratio move_freq_b2w, mcolor(navy%40)) ///
       (line median_poly_pre move_freq_b2w, sort lcolor(red) lwidth(medthick)) ///
       (rarea lower_poly_pre upper_poly_pre  move_freq_b2w, sort color(red%15)), ///
       title("Pre-Movement Black-White Incarceration Stability") ///
       subtitle("With nonlinear quantile regression prediction bands") ///
       xtitle("Movers, as Share of Black Population") ///
       ytitle("Black/White Incarceration Ratio") ///
       legend(order(1 "Observed Ratios" 2 "Median Fit" 3 "95% Prediction Band")) ///
       name(graph_qreg_poly, replace)

*Graph with Prediction Intervals: Change in Incarceration Rates 


// Median (50th percentile)
qreg ratio_change  move_freq_b2w move_freq_b2w_sq, q(.5)
predict median_poly_change

// Lower bound (2.5th percentile)
qreg ratio_change move_freq_b2w move_freq_b2w_sq, q(.025)
predict lower_poly_change

// Upper bound (97.5th percentile)
qreg ratio_change move_freq_b2w move_freq_b2w_sq, q(.975)
predict upper_poly_change

// Graph the results
twoway (scatter ratio_change move_freq_b2w, mcolor(navy%40)) ///
       (line median_poly_change move_freq_b2w, sort lcolor(red) lwidth(medthick)) ///
       (rarea lower_poly_change upper_poly_change move_freq_b2w, sort color(red%15)), ///
       title("Change in Disparity") ///
       subtitle("With nonlinear quantile regression prediction bands") ///
       xtitle("Movers, as Share of Black Population") ///
       ytitle("Change in Black/White Incarceration Ratio") ///
       legend(order(1 "Observed Ratios" 2 "Median Fit" 3 "95% Prediction Band")) ///
       name(Change_by_Movers2, replace)

***** SIMULATION THREE: Movers Have Incarceration Rates Similar to Destination Category 
clear all
set seed 12345

**** SIMULATION PROGRAM ****
capture program drop incarceration_sim
program define incarceration_sim, rclass
    // Input parameters
    args movers    /* Number of people moving in each direction */ ///
         inc_rate_b2w    /* Incarceration rate - Black to White movers */ ///
         inc_rate_w2b    /* Incarceration rate - White to Black movers */
         
    // Fixed incarceration rates for remainers
    local inc_rate_w = 0.001  // 0.1% for White remainers
    local inc_rate_b = 0.005  // 0.5% for Black remainers
    
    // Preserve current dataset
    preserve
    
    // Setup population numbers (total population = 10,000)
    local total_pop = 10000
    local b_pop = 1500        // Fixed Black population (15%)
    local w_pop = 8500        // Fixed White population (85%)
	
    
    // Calculate movement frequencies (for reporting purposes)
    local move_freq_b2w = `movers' / `b_pop'
    local move_freq_w2b = `movers' / `w_pop'
    
    // Create dataset with individual records
    clear
    set obs `total_pop'
    
    // Initial race assignment (1=Black, 0=White)
    gen black = (_n <= `b_pop')
    
    // Assign movers (individuals who change categories)
    gen mover = 0
    replace mover = 1 if black==1 & _n <= `movers'                    // Black to White movers
    replace mover = 2 if black==0 & _n > (10000 - `movers')              // Last movers White people
    
    // Post-movement race
    gen new_black = black
    replace new_black = 0 if mover==1    // Black to White
    replace new_black = 1 if mover==2    // White to Black
    
    // Assign EXPECTED incarceration value based on group membership
    gen incarcerated = 0

    // Instead of binary outcomes, assign expected values (probabilities)
    replace incarcerated = `inc_rate_b' if black==1 & mover==0    // Black remainers
    replace incarcerated = `inc_rate_w' if black==0 & mover==0    // White remainers
    replace incarcerated = `inc_rate_b2w' if mover==1             // Black to White movers
    replace incarcerated = `inc_rate_w2b' if mover==2             // White to Black movers
    
    // ================ PRE-MOVEMENT ANALYSIS ================
    // Calculate incarceration rates by ORIGINAL racial category (pre-movement)
    quietly summarize incarcerated if black==1
    local pre_black_inc_rate = r(mean)
    
    quietly summarize incarcerated if black==0
    local pre_white_inc_rate = r(mean)
    
    // Calculate incarceration rate ratio using original categories
    local pre_inc_ratio = `pre_black_inc_rate'/`pre_white_inc_rate'
    
    // ================ POST-MOVEMENT ANALYSIS ================
    // Calculate observed incarceration rates by POST-movement race
    quietly summarize incarcerated if new_black==1
    local post_black_inc_rate = r(mean)
    
    quietly summarize incarcerated if new_black==0
    local post_white_inc_rate = r(mean)
    
    // Calculate incarceration rate ratio after movement
    local post_inc_ratio = `post_black_inc_rate'/`post_white_inc_rate'
    
    // Calculate ratio change due to mobility
    local ratio_change = `post_inc_ratio' - `pre_inc_ratio'
    local ratio_change_pct = 100*(`post_inc_ratio' - `pre_inc_ratio')/`pre_inc_ratio'
    
    // Calculate proportion of each group post-movement
    qui count if new_black==1
    local final_black_n = r(N)
    qui count if new_black==0
    local final_white_n = r(N)
    
    // Calculate incarceration rates for each mobility pattern
    qui summarize incarcerated if black==1 & mover==0
    local black_remain_rate = r(mean)
    qui summarize incarcerated if black==0 & mover==0
    local white_remain_rate = r(mean)
    qui summarize incarcerated if mover==1
    local black_to_white_rate = r(mean)
    qui summarize incarcerated if mover==2
    local white_to_black_rate = r(mean)
    
    // Return results - both pre and post movement
    return scalar pre_inc_ratio = `pre_inc_ratio'
    return scalar post_inc_ratio = `post_inc_ratio'
    return scalar ratio_change = `ratio_change'
    return scalar ratio_change_pct = `ratio_change_pct'
    
    return scalar pre_black_inc_rate = `pre_black_inc_rate'
    return scalar pre_white_inc_rate = `pre_white_inc_rate'
    return scalar post_black_inc_rate = `post_black_inc_rate'
    return scalar post_white_inc_rate = `post_white_inc_rate'
    
    return scalar black_remain_rate = `black_remain_rate'
    return scalar white_remain_rate = `white_remain_rate'
    return scalar black_to_white_rate = `black_to_white_rate'
    return scalar white_to_black_rate = `white_to_black_rate'
    
    return scalar black_pct = `final_black_n'/`total_pop'
    return scalar white_pct = `final_white_n'/`total_pop'
    return scalar b_pop_original = `b_pop'
    return scalar w_pop_original = `w_pop'
    return scalar movers = `movers'
    return scalar move_freq_b2w = `move_freq_b2w'
    return scalar move_freq_w2b = `move_freq_w2b'
    
    // Restore original dataset
    restore
end

**** RUNNING SIMULATIONS USING POSTFILE ****

// Set up output file
tempfile sim_results
postfile sim_handle movers move_freq_b2w move_freq_w2b inc_rate_b2w inc_rate_w2b ///
                   pre_inc_ratio post_inc_ratio ratio_change ratio_change_pct ///
                   pre_black_inc_rate pre_white_inc_rate ///
                   post_black_inc_rate post_white_inc_rate ///
                   black_remain_rate white_remain_rate ///
                   black_to_white_rate white_to_black_rate ///
                   black_pct white_pct ///
                   using "`sim_results'", replace

// Generate parameter combinations
forvalues i = 1/10000 {
    // Generate random parameter values
    local movers = round(runiform(0, 750))     // Number of movers (0-750 people in each direction)
    local irb2w = runiform(0.00075, 0.00125)   // Incarceration rate for Black to White movers
    local irw2b = runiform(0.00375, 0.00625)   // Incarceration rate for White to Black movers
    
    // Run simulation with these parameters
    qui incarceration_sim `movers' `irb2w' `irw2b'
    
    // Store results
    post sim_handle (r(movers)) (r(move_freq_b2w)) (r(move_freq_w2b)) (`irb2w') (`irw2b') ///
                   (r(pre_inc_ratio)) (r(post_inc_ratio)) (r(ratio_change)) (r(ratio_change_pct)) ///
                   (r(pre_black_inc_rate)) (r(pre_white_inc_rate)) ///
                   (r(post_black_inc_rate)) (r(post_white_inc_rate)) ///
                   (r(black_remain_rate)) (r(white_remain_rate)) ///
                   (r(black_to_white_rate)) (r(white_to_black_rate)) ///
                   (r(black_pct)) (r(white_pct))
}

// Close postfile and load results
postclose sim_handle
use "`sim_results'", clear

**** ANALYSIS OF RESULTS ****

// Basic summary of pre- and post-movement incarceration ratios
summarize pre_inc_ratio post_inc_ratio ratio_change ratio_change_pct, detail

// Histogram of pre- and post-movement incarceration rate ratios
*histogram pre_inc_ratio, color(blue%30) bin(20) ///
    addplot(histogram post_inc_ratio, color(red%30) bin(20)) ///
    legend(order(1 "Pre-Movement" 2 "Post-Movement")) ///
    title("Distribution of Black-White Incarceration Ratios") ///
    subtitle("Before and After Mobility") name(hist_compare, replace)

// Histogram of ratio changes
*histogram ratio_change, bin(20) color(green%50) normal ///
    title("Change in Incarceration Rate Ratio Due to Mobility") ///
    subtitle("Positive values = mobility increases disparity") ///
    name(hist_change, replace)

// Examine relationship between mobility level and ratio change
*scatter ratio_change movers, name(scatter_change1, replace) ///
    title("Effect of Mobility on Incarceration Ratio Change") ///
    xtitle("Number of People Moving in Each Direction") ///
    ytitle("Change in Black/White Incarceration Ratio")

// Add fitted line to see trend    
*twoway (scatter ratio_change movers) (lowess ratio_change movers), ///
    name(scatter_change2, replace) ///
    title("Effect of Mobility on Incarceration Ratio Change") ///
    xtitle("Number of People Moving in Each Direction") ///
    ytitle("Change in Black/White Incarceration Ratio") ///
    legend(off)
    
// Effect of incarceration rates of movers on ratio change
*twoway (scatter ratio_change inc_rate_b2w) (lowess ratio_change inc_rate_b2w), ///
    name(graph_change1, replace) ///
    title("Effect of Black→White Movers' Inc. Rate on Ratio Change") ///
    xtitle("Black→White Movers' Incarceration Rate") ///
    ytitle("Change in Incarceration Ratio") legend(off)





// Display a compact summary of pre/post values by mobility level
*gen mobility_level = "Low" if movers < 250
*replace mobility_level = "Medium" if movers >= 250 & movers < 500
*replace mobility_level = "High" if movers >= 500

*label var pre_inc_ratio "Ratio Before Movement"
*label var post_inc_ratio "Ratio After Movement"
*label var ratio_change "Change in Ratio"
*label var ratio_change_pct "Percent Change"

*table mobility_level, statistic(mean pre_inc_ratio) statistic(mean post_inc_ratio) ///
                    statistic(mean ratio_change) statistic(mean ratio_change_pct) ///
                    statistic(count ratio_change)


// Verify 5:1 ratio is maintained for remainers
sum black_remain_rate white_remain_rate
gen remain_rate_ratio = black_remain_rate/white_remain_rate
summarize remain_rate_ratio

// Basic summary of observed incarceration rate ratios
summarize post_inc_ratio, detail


// Histogram of incarceration ratios 
histogram post_inc_ratio, bin(20) normal title("Distribution of Black-White Incarceration Ratios") ///
    subtitle("Equal numbers moving each way, Inc. rates 5%/1%") name(post_inc_ratio, replace)



// Effect of incarceration rates of movers
*Add prediction intervals) 
twoway (scatter post_inc_ratio inc_rate_b2w) (lowess post_inc_ratio inc_rate_b2w), ///
    name(post_by_b2w3, replace) title("Post-Movement Disparity, by Black-to-White Movers' Incarceration Rate") ///
    xtitle("Black-to-White Movers' Incarceration Rate") ///
    ytitle("Black/White Incarceration Ratio") legend(off)


twoway (scatter post_inc_ratio inc_rate_w2b) (lowess post_inc_ratio inc_rate_w2b), ///
    name(post_by_w2b3, replace) title("Post-Movement Disparity, by White-to-Black Movers' Incarceration Rate") ///
    xtitle("White-to-Black Movers' Incarceration Rate") ///
    ytitle("Black/White Incarceration Ratio") legend(off)

twoway (scatter pre_inc_ratio inc_rate_b2w) (lowess pre_inc_ratio inc_rate_b2w), ///
    name(pre_by_b2w3, replace) title("Pre-Movement Disparity, by Black-to-White Movers' Incarceration Rate") ///
    xtitle("Black-to-White Movers' Incarceration Rate") ///
    ytitle("Black/White Incarceration Ratio") legend(off)


twoway (scatter pre_inc_ratio inc_rate_w2b) (lowess pre_inc_ratio inc_rate_w2b), ///
    name(pre_by_w2b3, replace) title("Pre-Movement Disparity, by White-to-Black Movers' Incarceration Rate") ///
    xtitle("White-to-Black Movers' Incarceration Rate") ///
    ytitle("Black/White Incarceration Ratio") legend(off)
	

*twoway (scatter ratio_change inc_rate_b2w) (lowess ratio_change inc_rate_b2w), ///
    name(change_by_b2w, replace) title("Change in Disparity, by Black-to-White Movers' Incarceration Rate") ///
    xtitle("Black-to-White Movers' Incarceration Rate") ///
    ytitle("Change in Black/White Disparity") legend(off)

*twoway (scatter ratio_change inc_rate_w2b) (lowess ratio_change inc_rate_w2b), ///
    name(graph4, replace) title("Change in Disparity, by White-to-Black Movers' Incarceration Rate") ///
    xtitle("White-to-Black Movers' Incarceration Rate") ///
    ytitle("Change in Black/White Disparity") legend(off)

// Regression analysis of factors affecting the incarceration rate ratio
regress post_inc_ratio movers inc_rate_b2w inc_rate_w2b c.movers#c.inc_rate_w2b c.movers#c.inc_rate_b2w



*Graph with Prediction intervals: Post-Incarceration Rate 
	 

// Sort by x-variable
sort  move_freq_b2w

// Run quantile regressions with polynomial terms
gen  move_freq_b2w_sq =  move_freq_b2w^2

// Median (50th percentile)
qreg post_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.5)
predict median_poly_post 

// Lower bound (2.5th percentile)
qreg post_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.025)
predict lower_poly_post 

// Upper bound (97.5th percentile)
qreg post_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.975)
predict upper_poly_post 

// Graph the results
twoway (scatter post_inc_ratio move_freq_b2w, mcolor(navy%40)) ///
       (line median_poly_post  move_freq_b2w, sort lcolor(red) lwidth(medthick)) ///
       (rarea lower_poly_post upper_poly_post move_freq_b2w, sort color(red%15)), ///
       title("Post-Movement Black-White Incarceration, by Movers") ///
       subtitle("With nonlinear quantile regression prediction bands") ///
       xtitle("Movers, as Share of Black Population") ///
       ytitle("Black/White Incarceration Ratio") ///
       legend(order(1 "Observed Ratios" 2 "Median Fit" 3 "95% Prediction Band")) ///
       name(Disparity_by_Movers3, replace)
	  
*Graph with Prediction Intervals: Pre-Incarceration Rates 



// Median (50th percentile)
qreg pre_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.5)
predict median_poly_pre

// Lower bound (2.5th percentile)
qreg pre_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.025)
predict lower_poly_pre

// Upper bound (97.5th percentile)
qreg pre_inc_ratio  move_freq_b2w move_freq_b2w_sq, q(.975)
predict upper_poly_pre 

// Graph the results
twoway (scatter pre_inc_ratio move_freq_b2w, mcolor(navy%40)) ///
       (line median_poly_pre move_freq_b2w, sort lcolor(red) lwidth(medthick)) ///
       (rarea lower_poly_pre upper_poly_pre  move_freq_b2w, sort color(red%15)), ///
       title("Pre-Movement Black-White Incarceration, by Movers") ///
       subtitle("With nonlinear quantile regression prediction bands") ///
       xtitle("Movers, as Share of Black Population") ///
       ytitle("Black/White Incarceration Ratio") ///
       legend(order(1 "Observed Ratios" 2 "Median Fit" 3 "95% Prediction Band")) ///
       name(pre_movement_by_movers3, replace)

*Graph with Prediction Intervals: Change in Incarceration Rates 


// Median (50th percentile)
qreg ratio_change  move_freq_b2w move_freq_b2w_sq, q(.5)
predict median_poly_change

// Lower bound (2.5th percentile)
qreg ratio_change move_freq_b2w move_freq_b2w_sq, q(.025)
predict lower_poly_change

// Upper bound (97.5th percentile)
qreg ratio_change move_freq_b2w move_freq_b2w_sq, q(.975)
predict upper_poly_change

// Graph the results
twoway (scatter ratio_change move_freq_b2w, mcolor(navy%40)) ///
       (line median_poly_change move_freq_b2w, sort lcolor(red) lwidth(medthick)) ///
       (rarea lower_poly_change upper_poly_change move_freq_b2w, sort color(red%15)), ///
       title("Change in Disparity") ///
       subtitle("With nonlinear quantile regression prediction bands") ///
       xtitle("Movers, as Share of Black Population") ///
       ytitle("Change in Black/White Incarceration Ratio") ///
       legend(order(1 "Observed Ratios" 2 "Median Fit" 3 "95% Prediction Band")) ///
       name(change_by_movers3, replace)