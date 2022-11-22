#![allow(dead_code)]
#![allow(unused_variables)]

fn ln_exp_sum(exponents: &Vec<f64>) -> f64 {
    exponents.iter().fold(0f64, |acc, val| acc + val.exp()).ln()
}

fn cost(fee: f64, balances: &Vec<f64>) -> f64 {
    let fee_times_sum = fee * balances.iter().sum::<f64>();
    let exponents = balances.iter().map(|e| e / fee_times_sum).collect();
    fee_times_sum * ln_exp_sum(&exponents)
}

fn price(fee: f64, balances: &Vec<f64>, balance_in_question: f64) -> f64 {
    let balance_sum = balances.iter().sum::<f64>();
    let fee_times_sum = fee * balance_sum;
    let balance_exponential_results: Vec<f64> = balances.iter().map(|qj| (qj / fee_times_sum).exp()).collect();
    let left_from_addition = cost(fee, balances) / balance_sum;
    // println!("--------- price function ------------");
    // println!("left_from_addition: {}", left_from_addition);
    let numerator_left_from_minus = (balance_in_question / fee_times_sum).exp() * balance_sum;
    // println!("numerator_left_from_minus: {}", numerator_left_from_minus);
    let numerator_right_from_minus: f64 = balance_exponential_results.iter().enumerate().map(|(idx, val)| balances[idx] * val).sum();
    // println!("numerator_right_from_minus: {}", numerator_right_from_minus);
    let numerator = numerator_left_from_minus - numerator_right_from_minus;
    // println!("numerator: {}", numerator);
    let denominator: f64 = balance_exponential_results.iter().sum::<f64>() * balance_sum;
    // println!("denominator: {}", denominator);
    // println!("---------      end      ------------");
    left_from_addition + (numerator / denominator)
}

fn price_first_quotient(fee: f64, balances: &Vec<f64>, balance_in_question: f64) -> f64 {
    let balance_sum = balances.iter().sum::<f64>();
    let fee_times_sum = fee * balance_sum;
    let balance_exponential_results: Vec<f64> =
    balances.iter().map(|qj| (qj / fee_times_sum).exp()).collect();
    let denominator: f64 = balance_exponential_results.iter().sum::<f64>() * balance_sum;
    ((balance_in_question / fee_times_sum).exp() * balance_sum) / denominator
}

fn price_second_quotient(fee: f64, balances: &Vec<f64>, balance_in_question: f64) -> f64 {
    let balance_sum = balances.iter().sum::<f64>();
    let fee_times_sum = fee * balance_sum;
    let balance_exponential_results: Vec<f64> =
    balances.iter().map(|qj| (qj / fee_times_sum).exp()).collect();
    let denominator: f64 = balance_exponential_results.iter().sum::<f64>() * balance_sum;
    balance_exponential_results.iter().enumerate().map(|(idx, val)| balances[idx] * val).sum::<f64>() / denominator
}

fn price2(fee: f64, balances: &Vec<f64>, balance_in_question: f64) -> f64 {
    let balance_sum = balances.iter().sum::<f64>();
    let left_from_addition = cost(fee, balances) / balance_sum;
    let first_quotient = price_first_quotient(fee, balances, balance_in_question);
    let second_quotient: f64 = price_second_quotient(fee, balances, balance_in_question);
    left_from_addition + first_quotient - second_quotient
}

fn sigmoid_fee(m: f64, n: f64, p: f64, r: f64) -> f64 {
    (m * (r - n)) / (p + (r - n).powi(2)).sqrt()
}

const FEE: f64 = 0.1;

fn compare_prices(quantities: Vec<f64>, amount: f64, asset_index: usize, debug: bool) {
    let cost_before = cost(FEE, &quantities);
    if !debug { println!("quantities, amount, index: {:?}, {}, {}", quantities, amount, asset_index) };
    if debug { println!("Fee: {}", FEE); }
    if debug { println!("Balances (quantities) before: {:?}", quantities) };
    if debug { println!("cost_before: {}", cost_before) };
    if debug { println!("BUY {}", amount) };
    let quantities_after = vec![500f64, quantities[asset_index] - amount];
    let cost_after = cost(FEE, &quantities_after);
    if debug { println!("Balances (quantities) after: {:?}", quantities_after) };
    if debug { println!("cost_after: {}", cost_after) };
    println!("exchange cost using cost strategy: {}", cost_before - cost_after);
    println!("exchange cost using price formula: {}", price(FEE, &quantities, quantities[1]) * amount);
    println!("prices: {}", price(FEE, &quantities, quantities[1]))
}

fn main() {
    //compare_prices(vec![500.0, 500.0], 250.0, 1, false);
    compare_prices(vec![500.0, 500.0], 250.0, 1, false);
    
    // let's see how much we have to pay to move [0,0] to [10,0]
    let fee = 0.005;
    let v1 = vec![10f64; 2];
    let v2 = vec![20f64, 10f64];
    let v5 = vec![20f64; 2];
    let v3 = vec![1000f64; 2];
    let v4 = vec![1010f64, 1000f64];
    /*
    let first_cost = cost(fee, &v2) - cost(fee, &v1);
    let second_cost = cost(fee, &v4) - cost(fee, &v3);
    println!("first_cost (initial liquidity [10,10], buy 10): {}\nsecond_cost (initial liquidity [1000,1000], buy 10): {}", first_cost, second_cost);
    println!("{}", cost(fee, &v5) - cost(fee, &v1));
    let v6 = vec![973.022099f64; 4];
    println!("Cost should be 1000: {}", cost(0.005, &v6));
    */
    println!("Cost with fee 0.1: {}\nCost with fee 0.001: {}", cost(0.1, &v3), cost(0.001, &v3));
    println!("Price with fee 0.1: {}\nPrice with fee 0.001: {}", price(0.1, &v3, v3[0]), price(0.001, &v3, v3[0]));
    println!("Sigmoid fee with r=1: {}", sigmoid_fee(0.01, 0.0, 2.0, 0.000000001));
}
