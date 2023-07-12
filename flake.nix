{
  inputs = {
    ros2nix.url = "github:pylgos/ros2nix";
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.follows = "ros2nix/nixpkgs";
  };

  outputs = { self, nixpkgs, ros2nix, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      rosPkgs = ros2nix.legacyPackages.${system}.humble;
      py = pkgs.python310Packages;
      lib = pkgs.lib;
    in {
      packages.colcon_ros_nimble = py.buildPythonPackage {
        pname = "colcon_ros_nimble";
        version = "0.1.0";
        propagatedBuildInputs = [
          rosPkgs.systemPackages.python3-colcon-common-extensions
          py.flake8
          py.flake8-blind-except
          py.flake8-docstrings
          py.flake8-import-order
          py.pep8-naming
          py.pyenchant
          py.pylint
          py.pytest
          py.pytest-cov
        ];
        src = lib.cleanSource ./.;
      };

      packages.default = self.packages.${system}.colcon_ros_nimble;
    });
}
