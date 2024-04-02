#!/bin/bash

# Sum Egamma
cd egamma2018a_output/
../hadddir */*

cd ../egamma2018b_output/
../hadddir */*

cd ../egamma2018c_output/
../hadddir */*

cd ../egamma2018d_output/
../hadddir */*
cd ..

hadd summed_egamma_all.root egamma2018a_output/summed.root egamma2018b_output/summed.root egamma2018c_output/summed.root egamma2018d_output/summed.root
