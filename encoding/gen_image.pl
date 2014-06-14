#!/usr/bin/perl

use v5.14;
use Image::Magick;

my $self;
$self->{title_output} = $ARGV[0];
$self->{title_text} = $ARGV[1];
create_title();

sub create_title {
  my $im;
  $im = new Image::Magick;
  
  $im->Set( size => '768x200' );
  $im->ReadImage("./blank_title.png");
  
  my $label=Image::Magick->new(size=>"700x200");
  $label->Set(gravity => "Center", font => '/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf', background => 'none', fill => 'white');
  $label->Read("label:$self->{title_text}");
  $im->Composite(image => $label, gravity => 'Center');
  $im->Write("$self->{title_output}");
}
