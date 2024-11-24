#!/usr/bin/perl
use strict;
use warnings;
use Data::Dumper;
use File::Basename;

my @files=<$ARGV[0]>;
<<<<<<< HEAD
my @fields = ("Eukaryota","Bacteria","Fungi","Archaea","Viruses","Homo sapiens","unclassified");  #Defining fields
=======
my @fields = ("Bacteria","Fungi","Archaea","Viruses","Homo sapiens","Unclassified");  #Defining fields
>>>>>>> b38db8b (Initial commit for v2 prod version)

my $out = {};
foreach my $file (@files) {

open FH,$file or die "Cannot open file $file: $!\n";

my $read_count = 0;
while (<FH>) {
chomp;
my @tmp_f = split(/\t/);
my $value = $tmp_f[5];
my $rc = $tmp_f[1];
$value=~s/^\s*//g;
#print "val = $value\n";
<<<<<<< HEAD
if ($value eq "root" or $value eq "unclassified") {
=======
if ($value eq "root" or $value eq "Unclassified") {
>>>>>>> b38db8b (Initial commit for v2 prod version)
$read_count += $rc;
}
if (scalar grep {$_ eq $value} @fields) {
my $percent = $tmp_f[0];
#print join("\t",$value,$percent);
#print "\n";
$out->{$file}->{percent}->{$value} = $percent
}
}
$out->{$file}->{read_count} = $read_count;
}
close FH;

#print "Sample_name\t";
#my $sid= basename($files[0]);
#$sid=~s/_kraken.txt//g;
#print $sid."\n";
print "Read count\t";
print $out->{$files[0]}->{read_count}."\n";
foreach my $h (@fields) {
print "$h\t";
my $p = $out->{$files[0]}->{percent};
if (exists $p->{$h}) {
print $p->{$h}."\n";
}else {
print "0\n";
}
}
