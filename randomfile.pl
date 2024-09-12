$rnd=int(rand()*10000);
$filename=$rnd . ".pkl";
open(my $fh, ">", $filename);
print $fh "hello";
close($fh);
