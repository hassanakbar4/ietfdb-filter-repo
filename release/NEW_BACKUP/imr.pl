#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

$MYSQL = 2;

($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null) = init_database($MYSQL);

unless (defined ($ARGV[1])) {
   die "Usage: imr <start date> <end data> [-long]\n";
}

$start_date = convert_date($ARGV[0],$CONVERT_SEED);
$end_date = convert_date($ARGV[1],$CONVERT_SEED);

$dsd = convert_date($start_date,2);
$ded = convert_date($end_date,2);
$dsd = convert_date($dsd,4);
$ded = convert_date($ded,4);
$start_date = db_quote($start_date);
$end_date = db_quote($end_date);
print "\t\t IETF Progress Report\n\t\t $dsd to $ded\n\n";

$section_count = 0;

#  IESG Protocol Action
$sqlStr = "select count(id_document_tag) from internet_drafts where b_approve_date >= $start_date and b_approve_date <= $end_date and b_approve_date is not null and b_approve_date <> ''";
$exist_count = db_select($sqlStr);
report_protocol_action($exist_count) if ($exist_count > 0);

#IESG Last Call Issued to the IETF
$sqlStr = "select count(id_document_tag) from internet_drafts where lc_sent_date >= $start_date and lc_sent_date <= $end_date and lc_sent_date is not null and lc_sent_date <> ''";
$exist_count = db_select($sqlStr);
report_last_call($exist_count) if ($exist_count > 0);

#New Working Groups
$sqlStr = "select count(group_acronym_id) from groups_ietf where start_date >= $start_date and start_date <= $end_date and start_date is not null and start_date <> '' and group_type_id = 1";
$exist_count = db_select($sqlStr);
report_new_wg($exist_count) if ($exist_count > 0);

#Concluded Working Groups
$sqlStr = "select count(group_acronym_id) from groups_ietf where concluded_date >= $start_date and concluded_date <= $end_date and concluded_date is not null and concluded_date <> ''";
$exist_count = db_select($sqlStr);
report_concluded_wg($exist_count) if ($exist_count > 0);

#Internet-Drafts Actions
$sqlStr = "select count(id_document_tag) from internet_drafts where revision_date >= $start_date and revision_date <= $end_date and revision_date is not null and revision_date <> '' and filename not like 'rfc%'";
$exist_count = db_select($sqlStr);
report_id_action($exist_count) if ($exist_count > 0);

#RFC Produced
$sqlStr = "select count(rfc_number) from rfcs where rfc_published_date >= $start_date and rfc_published_date <= $end_date and rfc_published_date is not null and rfc_published_date <> ''";
$exist_count = db_select($sqlStr);
report_rfc_produced($exist_count) if ($exist_count > 0);

#List of Active Working Groups
#report_active_wg() if (defined($ARGV[2]) and $ARGV[2] eq "-long");



exit;



sub report_protocol_action {
  my $item_count = shift;
  $section_count++;
  print " $section_count) $item_count IESG Protocol Actions this period\n ";
  print "\n";
  my $sqlStr = "select id_document_name, intended_status_id,status_id,rfc_number from internet_drafts where b_approve_date >= $start_date and b_approve_date <= $end_date and b_approve_date is not null and b_approve_date <> ''";
  my @List = db_select_multiple($sqlStr);

  for $array_ref (@List) {
    my ($id_document_name,$intended_status_id,$status_id,$rfc_number) = rm_tr(@$array_ref);
    if ($status_id == 3) {
      ($id_document_name,$intended_status_id) = rm_tr(db_select("select rfc_name,intended_status_id from rfcs where rfc_number = $rfc_number"));
      $intended_status_value = get_intended_status_value($intended_status_id,"RFC");
    } else {
      $intended_status_value = get_intended_status_value($intended_status_id,"ID");
    }
    $id_document_name = indent_text($id_document_name,4);
    print "$id_document_name ($intended_status_value)\n\n";
  }
  return;
}

sub report_last_call {
  my $item_count = shift;
  $section_count++;
  print " $section_count) $item_count IESG Last Calls issued to the IETF this period\n ";
  print "\n";
  my $sqlStr = "select id_document_name,intended_status_id,status_id,rfc_number,filename,revision from internet_drafts where lc_sent_date >= $start_date and lc_sent_date <= $end_date and lc_sent_date is not null and lc_sent_date <> ''";
  my @List = db_select_multiple ($sqlStr);

  for $array_ref (@List) {
    my ($id_document_name,$intended_status_id,$status_id,$rfc_number,$filename,$revision) = rm_tr(@$array_ref);
    if ($status_id == 3) {
      ($id_document_name,$intended_status_id) = rm_tr(db_select("select rfc_name,intended_status_id from rfcs where rfc_number = $rfc_number"));
      $intended_status_value = get_intended_status_value($intended_status_id,"RFC");
      $filename = "RFC${rfc_number}";
    } else {
      $intended_status_value = get_intended_status_value($intended_status_id,"ID");
      $filename .= "-${revision}";
    }
    $id_document_name = indent_text($id_document_name,4);
    print "$id_document_name\n\t<$filename> ($intended_status_value)\n\n";
  }

  return;
}

sub report_new_wg {
  my $item_count = shift;
  $section_count++;
  print " $section_count) $item_count New Working Group(s) formed this period\n ";
  print "\n";
  my $sqlStr = "select acronym,name from groups_ietf, acronym where group_acronym_id = acronym_id and start_date >= $start_date and start_date <= $end_date and start_date is not null and start_date <> '' and group_type_id = 1";
  my @List = db_select_multiple($sqlStr);
  for $array_ref (@List) {
    my ($group_acronym,$group_name) = rm_tr(@$array_ref);
    $group_name = indent_text($group_name,4);
    print "$group_name ($group_acronym)\n\n";
  }
  return;
}

sub report_concluded_wg {
  my $item_count = shift;
  $section_count++;
  print " $section_count) $item_count Working Group(s) concluded this period\n ";
  print "\n";
  my $sqlStr = "select acronym,name from groups_ietf, acronym where group_acronym_id = acronym_id and concluded_date >= $start_date and concluded_date <= $end_date and concluded_date is not null and concluded_date <> ''";
  my @List = db_select_multiple($sqlStr);
  for $array_ref (@List) {
    my ($group_acronym,$group_name) = rm_tr(@$array_ref);
    $group_name = indent_text($group_name,4);
    print "$group_name ($group_acronym)\n\n";
  }

  return;
}

sub report_id_action {
  my $item_count = shift;
  $section_count++;
  print " $section_count) $item_count new or revised Internet-Drafts this period\n ";
print qq {
 (o - Revised Internet-Draft; + - New Internet-Draft)

   WG		I-D Title	<Filename>
 -------    ------------------------------------------
};
  my $sqlStr = "select acronym,id_document_name,filename,revision from internet_drafts, acronym where group_acronym_id = acronym_id and revision_date >= $start_date and revision_date <= $end_date and revision_date is not null and revision_date <> '' and filename not like 'rfc%'";
  my @List = db_select_multiple($sqlStr);
  for $array_ref(@List) {
    my ($group_acronym,$id_document_name,$filename,$revision) = rm_tr(@$array_ref);
    $id_document_name = indent_text2($id_document_name,14);
    $filename = "<$filename-$revision.txt>";
    $filename = indent_text($filename,18);
    $group_acronym = "($group_acronym)";
    $group_acronym = add_spaces($group_acronym,10);
    my $old_or_new = "o";
    $old_or_new = "+" if ($revision eq "00");
    print "$group_acronym $old_or_new  $id_document_name\n$filename\n";

  } 
  print "\n";
  return;
}

sub report_rfc_produced {
  my $item_count = shift;
  $section_count++;
  print " $section_count) $item_count RFC produced this period\n ";
print qq {
    S - Standard;	PS - Proposed Standard; DS - Draft Standard;
    B - Best Current Practices; E - Experimental; I - Informational

 RFC   Stat  WG       Published	   Title
------- -- --------   ---------- -----------------------------------------
};

  my @status_ary = ('','PS','DS','S ','E ','I ','B ','H ','N ');

  my $sqlStr = "select rfc_number,status_id,group_acronym,rfc_published_date,rfc_name from rfcs where rfc_published_date >= $start_date and rfc_published_date <= $end_date and rfc_published_date is not null and rfc_published_date <> ''";
  my @List = db_select_multiple($sqlStr);
  my $s_count = 0;
  my $bcp_count = 0;
  my $e_count = 0;
  my $i_count = 0;

  for $array_ref (@List) {
    my ($rfc_number,$status_id,$group_acronym,$pDate,$rfc_name) = rm_tr (@$array_ref);
    $pDate = convert_date($pDate,2);
    $pDate = convert_date($pDate,3);
    if ($status_id == 3) {
      $s_count++;
    } elsif ($status_id == 4) {
      $e_count++;
    } elsif ($status_id == 5) {
      $i_count++;
    } elsif ($status_id == 6) {
      $bcp_count++;
    }
    my $si = $status_ary[$status_id];
    $rfc_name = indent_text2($rfc_name,33);
    $group_acronym = "($group_acronym)";
    $group_acronym = add_spaces($group_acronym,10);
    print "RFC$rfc_number $si $group_acronym $pDate     $rfc_name\n";  
  }
  print "\n";
  print "   $s_count Standards Track;  $bcp_count BCP;  $e_count Experimental;  $i_count Informational\n\n";
  return;
}

sub report_active_wg {
  $section_count++;
  print " $section_count) Active Working Groups this period\n ";
  print "\n";

  return;
}


