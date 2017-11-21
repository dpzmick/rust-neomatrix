#!/usr/bin/env python2
import argparse
import time
import toml

# generate a script which will run the entire benchmark suite and format the
# output

class CompilerConfig(object):
    """
    A single cpu architecture that the lib might be tested against (in terms
    of llvm platforms)
    """
    def __init__(self, cpu, rustc_args, unsupported_features):
        self.cpu = cpu
        self.rustc_args = rustc_args
        self.unsupported_features = unsupported_features

    def generate_RUSTFLAGS(self):
        """
        The only way to set rustc flags is apparently with the RUSTFLAGS
        environment variable. This generates those flags for the config given.
        """
        return 'RUSTFLAGS=\'{}\''.format(self.rustc_args)

    def __str__(self):
        return \
            'CompilerConfig {{cpu={}, rustc_args={}, unsupported_features={}}}' \
            .format(self.cpu, self.rustc_args, self.unsupported_features)

class MatrixCargoConfig(object):
    """
    Responsible for all TOML parsing and creation of objects from the Matrix
    cargo config file
    """
    def __init__(self, filename):
        self._toml = None

        with open(filename, 'r') as toml_data:
            self._toml = toml.loads('\n'.join(toml_data.readlines()))

        if self._toml is None:
            raise ValueError("failed to open file!")

    @property
    def features(self):
        return self._toml['features'].keys()

    @property
    def global_env_vars(self):
        return self._toml['package']['metadata']['global_environment']

    @property
    def complier_configs(self):
        for cpu, data in self._toml['package']['metadata']['config'].iteritems():
            yield CompilerConfig(
                cpu,
                rustc_args=data['args'],
                unsupported_features=data.get('unsupported-features', []),
            )

        expected_keys = set( ('args', 'unsupported-features') )
        for key in data.keys():
            if key not in expected_keys:
                raise ValueError("unexpected key {} in metadata for {}".format(
                    key, cpu))

class BencmarkConfig(object):
    def __init__(self, compiler_config, feature_list):
        self._requested_features = set(feature_list)
        self._compiler_config = compiler_config

    def valid(self):
        return self._requested_features.isdisjoint(
            self._compiler_config.unsupported_features)

    def command(self):
        return '{} cargo bench {} {}'.format(
            self._compiler_config.generate_RUSTFLAGS(),
            '--features' if self._requested_features else '',
            ','.join(self._requested_features),
        )

    def canonical_name(self):
        return '{}{}'.format(
            self._compiler_config.cpu,
            ''.join(['_' + f for f in self._requested_features]),
        )

    # operator bool
    def __nonzero__(self):
        return self.valid()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark Script Generator")
    parser.add_argument(
        "--toml", help="Cargo.toml file to use", default="../Cargo.toml")

    parser.add_argument(
        "--output_dir",
        help="Output dir to use when generating benchmarks. Defaults to epoch")

    args = parser.parse_args()

    m = MatrixCargoConfig(args.toml)
    output_dir = args.output_dir or "output_{}".format(int(time.time()))

    assert len(m.features) <= 1, \
            "script doesn't support more than one feature"

    # TODO add a clean step
    # TODO add the global environment
    # TODO save script in output dir
    # TODO die on any error in generated script

    print '#!/bin/bash'
    print "mkdir -p {}".format(output_dir)

    for compiler_config in m.complier_configs:
        for feature_list in [[f] for f in m.features] + [[]]:
            bc = BencmarkConfig(compiler_config, feature_list)
            if bc:
                print '{} | ./cargo_bench_to_csv.py > {}/{}.csv'.format(
                    bc.command(),
                    output_dir,
                    bc.canonical_name(),
                )

    print "./generate_report.py {} {}".format(output_dir, output_dir)
    print "xdg-open {}/report.pdf".format(output_dir)
