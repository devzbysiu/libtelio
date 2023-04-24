#![deny(missing_docs)]
#![allow(unused_imports)]
#![cfg_attr(docsrs, feature(doc_cfg))]

//! Interface between [WireGuard](https://wireguard.com/) and the telio library

pub(crate) mod adapter;
pub(crate) mod wg;
pub(crate) mod windows;

pub mod uapi;

pub use crate::{
    adapter::{AdapterType, Error, FirewallCb, Tun},
    wg::*,
};
