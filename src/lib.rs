#![feature(cfg_target_feature)]
#![feature(iterator_step_by)]
#![feature(specialization)]
#![feature(test)]

#[cfg(feature = "vectorized")]
extern crate simd;

#[cfg(test)]
extern crate test;

// private modules
mod vector;

// public modules and exports
pub mod matrix;
pub use matrix::*;
