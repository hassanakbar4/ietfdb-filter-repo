#!/usr/local/bin/perl -w

use lib '/home/mlee/RELEASE';
use lib '/export/home/mlee/RELEASE';

use IETF_DBUTIL;
use IETF_UTIL;

my $usage_str = qq {
   USAGE: idabstracts.pl -[mysql|informix] <-area [area acronym]> 

};


die $usage_str unless (defined($ARGV[0]));
die $usage_str if ($ARGV[0] ne "-mysql" and  $ARGV[0] ne "-informix");

$db_mode = 0;
$INFORMIX = 1;
$MYSQL = 2;
$CURRENT_DATE = "CURRENT_DATE";
$CONVERT_SEED = 1;

if ($ARGV[0] eq "-mysql") {
   $db_mode = $MYSQL;
   $db_name = "ietf";
} else {
   $db_mode = $INFORMIX;
   $ENV{"DBPATH"} = "/usr/informix/databases";
   $db_name = "people";
   $CURRENT_DATE = "TODAY";
   $CONVERT_SEED = 2;
}
$ENV{"DBNAME"} = $db_name;
my $area_acronym_id;
my $id_index = 0;
if (defined($ARGV[1])) {
   if ($ARGV[1] eq "-area") {
      die $usage_str unless (defined($ARGV[2]));
      my $area_acronym = db_quote($ARGV[2]);
      $area_acronym_id = db_select("select acronym_id from acronym where acronym = $area_acronym");
      die "INVALID AREA ACRONYM $area_acronym\n\n"  unless ($area_acronym_id);
      $id_index = 1 if (defined($ARGV[3]) and $ARGV[3] eq "-idindex");
   } elsif ($ARGV[1] eq "-idindex") {
      $id_index = 1;
      if (defined($ARGV[2])) {
         die $usage_str unless ($ARGV[2] eq "-area");
	 die $usage_str unless (defined($ARGV[3]));
	 my $area_acronym = db_quote($ARGV[3]);
	 $area_acronym_id = db_select("select acronym_id from acronym where acronym = $area_acronym");
	 die "INVALID AREA ACRONYM $area_acronym\n\n"  unless ($area_acronym_id);
      }
   } else {
      die $usage_str;
   }
}
my $text_header;
if ($id_index == 0) {
$text_header = qq {              Current Internet-Drafts

     This summary sheet provides a short synopsis of each Internet-Draft
available within the "internet-drafts" directory at the shadow
sites directory.  These drafts are listed alphabetically by working
group acronym and start date.


};
} else {
$text_header = qq {              Current Internet-Drafts
   This summary sheet provides an index of each Internet-Draft
These drafts are listed alphabetically by Working Group acronym and
initial post date.


};
}
print $text_header;
my $sqlStr;
my $area_where = "";
if (defined($area_acronym_id)) {
   $area_where = "AND i.group_acronym_id IN\n(";
   my @subList = db_select_multiple("select group_acronym_id from area_group where area_acronym_id = $area_acronym_id");
   for $array_ref (@subList) {
      my ($id) = @$array_ref;
      $area_where .= "$id,";
   }
   chop($area_where);
   $area_where .= ")\n";
}
  $sqlStr = qq {
select a.name,a.acronym,i.id_document_name,i.id_document_tag,i.revision_date,
i.filename,i.file_type,i.abstract,i.start_date,i.revision
from acronym a, internet_drafts i
where a.acronym_id = i.group_acronym_id
AND i.status_id = 1
AND filename not like 'rfc%'
$area_where
order by a.acronym,i.start_date
};
my @List = db_select_multiple($sqlStr);
my $current_acronym = "undefined";
for $array_ref (@List) {
   my ($a_name,$acronym,$id_document_name,$id_document_tag,$revision_date,
   $filename,$file_type,$abstract,$start_date,$revision) = @$array_ref;
   ($a_name,$acronym,$id_document_name,$revision_date,$filename,$file_type,$abstract,$start_date) = rm_tr($a_name,$acronym,$id_document_name,$revision_date,$filename,$file_type,$abstract,$start_date);
   if ($acronym ne $current_acronym) {
      $current_acronym = $acronym;
      print "$a_name ($acronym)\n";
      my $dot_length = length($a_name) + length($acronym) + 3;
      for (my $loop=0;$loop<$dot_length;$loop++) {
         print "-"; 
      }
      print "\n\n";
   }
   $file_type = get_file_type($file_type);
   my $author_name = get_author_name($id_document_tag);
   $revision_date = convert_date($revision_date,2);
   $revision_date = convert_date($revision_date,4);
   my $bibl = qq {"$id_document_name", $author_name, $revision_date, <${filename}-${revision}${file_type}>};
   $bibl = indent_text($bibl,2);
   if ($id_index == 1) {
      $abstract = "";
   } else {
   $abstract = "\n" . indent_text($abstract,4);
   $abstract .= "\n";
   }
   print qq {$bibl
$abstract
};

}

print "\n";
exit;


sub get_file_type {
   my $file_type = shift;
   $_ = $file_type;
   my $ret_val=".txt";
   return $ret_val unless (/txt/);
   if (/ps/) {
      $ret_val .= ",.ps";
   }
   if (/pdf/) {
      $ret_val .= ",.pdf";
   }
   return $ret_val;
}



sub get_author_name {
   my $id_document_tag = shift;
   my $sqlStr = qq {
   select p.first_name,p.last_name from person_or_org_info p, id_authors i
   where i.id_document_tag = $id_document_tag
   AND i.person_or_org_tag = p.person_or_org_tag
   };
   my @List = db_select_multiple($sqlStr);
   my $ret_val = "";
   for $array_ref (@List) {
      my ($firstname,$lastname) = rm_tr(@$array_ref);
      $ret_val .= "$firstname $lastname, ";
   }
   chop $ret_val;
   chop $ret_val;
   return $ret_val;

}


