use std::ops::{Mul, Add};

#[cfg(feature = "vectorized")]
use simd;

// provide a stub of the simd module, since the module only supports simd
// platforms
#[cfg(not(feature = "vectorized"))]
mod simd {
    pub trait Simd { }
}

pub trait Vectorizable:  Mul<Output=Self> + Add<Output = Self> + Clone + Default {
    type SimdType: simd::Simd + Mul<Output=Self::SimdType>;

    fn vector_size() -> usize;
    fn load(arr: &[Self], idx: usize) -> Self::SimdType;
    fn extract(this: &Self::SimdType, element: u32) -> Self;
}

#[cfg(feature = "vectorized")]
mod vector_impls {
    use super::*;

    #[cfg(not(target_feature = "avx"))]
    impl Vectorizable for f32 {
        type SimdType = simd::f32x4;

        #[inline]
        fn vector_size() -> usize { 4 }

        #[inline]
        fn load(arr: &[Self], idx: usize) -> Self::SimdType
        {
            Self::SimdType::load(arr, idx)
        }

        #[inline]
        fn extract(this: &Self::SimdType, element: u32) -> Self
        {
            this.extract(element)
        }
    }

    #[cfg(not(target_feature = "avx"))]
    impl Vectorizable for i32 {
        type SimdType = simd::i32x4;

        #[inline]
        fn vector_size() -> usize { 4 }

        #[inline]
        fn load(arr: &[Self], idx: usize) -> Self::SimdType
        {
            Self::SimdType::load(arr, idx)
        }

        #[inline]
        fn extract(this: &Self::SimdType, element: u32) -> Self
        {
            this.extract(element)
        }
    }

    #[cfg(target_feature = "avx")]
    use simd::x86::avx;

    #[cfg(target_feature = "avx")]
    impl Vectorizable for f32 {
        type SimdType = avx::f32x8;

        #[inline]
        fn vector_size() -> usize { 8 }

        #[inline]
        fn load(arr: &[Self], idx: usize) -> Self::SimdType
        {
            Self::SimdType::load(arr, idx)
        }

        #[inline]
        fn extract(this: &Self::SimdType, element: u32) -> Self
        {
            this.extract(element)
        }
    }

    #[cfg(target_feature = "avx")]
    impl Vectorizable for i64 {
        type SimdType = avx::i64x4;

        #[inline]
        fn vector_size() -> usize { 4 }

        #[inline]
        fn load(arr: &[Self], idx: usize) -> Self::SimdType
        {
            Self::SimdType::load(arr, idx)
        }

        #[inline]
        fn extract(this: &Self::SimdType, element: u32) -> Self
        {
            this.extract(element)
        }
    }
}
