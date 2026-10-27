# Firmware

Firmware for the programmable chips of this project. All custom software in OpenDAP is written in Rust.

## Layout

- `<chip>/`: one folder per programmable chip, each a self-contained Rust project with its own target configuration (`.cargo/config.toml`, `rust-toolchain.toml`).

Which chips are programmable, and their targets, are not defined yet.
