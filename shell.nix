{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "oeispy-dev";

  # Packages available in the environment
  packages = with pkgs; [
    python3
    uv
    
    # Dependencies for building python extensions
    primesieve
    gmp
    mpfr
    libmpc
    pkg-config
  ];

  # Environment variables to help pip/uv find the headers and libs
  shellHook = ''
    # For primesieve (C++ dependency)
    export CPLUS_INCLUDE_PATH="${pkgs.primesieve.dev}/include:$CPLUS_INCLUDE_PATH"
    export LIBRARY_PATH="${pkgs.primesieve.lib}/lib:$LIBRARY_PATH"

    # For gmpy2 (C dependencies)
    export C_INCLUDE_PATH="${pkgs.gmp.dev}/include:${pkgs.mpfr.dev}/include:${pkgs.libmpc}/include:$C_INCLUDE_PATH"
    export LIBRARY_PATH="${pkgs.gmp}/lib:${pkgs.mpfr}/lib:${pkgs.libmpc}/lib:$LIBRARY_PATH"

    echo "Welcome to the oeispy development shell!"
    echo "Libraries (primesieve, gmp, etc.) are configured for build."
  '';
}
