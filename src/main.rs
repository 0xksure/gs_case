use std::path::Path;

use netcdf;
fn main() {
    let wave_data_path = Path::new("~/Downloads/waves_2019-01-01.nc");
    let file = netcdf::open(wave_data_path).expect("could not open file");
    let mut var = file.variables();
    let first_val = var.next().expect("could not get first val");
    println!("first val: {:?}", first_val);
}
