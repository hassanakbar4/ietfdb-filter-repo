#!/usr/bin/perl

##########################################################################
# Copyright © 2004 and 2003, Foretec Seminars, Inc.
##########################################################################
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL_NEW;
use GEN_UTIL;
use IETF;
use CGI;
use CGI_UTIL;
$host = $ENV{SCRIPT_NAME};
$devel_mode = ($host =~ /devel/)?1:0;
$db_name = ($devel_mode)?"develdb":"ietf";
$mode_text = ($devel_mode)?"Development Mode":"";
                                                                                                                
init_database($db_name);
$dbh=get_dbh();

my $q = new CGI;
print qq{Content-type: text/html

<html>
<head><title>IPR Detail Page $mode_text</title></head>
<body>
};

############################ Global Variables ####################
my $form_header_post = "<form action=\"ipr_admin_detail.cgi\" method=\"post\">";
my $font_color1 = qq{<font color="000000" face="Arial" Size=3>};
my $font_color2 = qq{<font color="333366" face="Arial" Size=2>};
############################# Global Variables ######################

my $command = $q->param("command");
my $ipr_id = $q->param("ipr_id");
unless (my_defined($command)) {
  ipr_detail_display($ipr_id);
  my $to_update_other_ipr=db_select($dbh,"select count(id) from ipr_updates where processed=0 and ipr_id=$ipr_id");
  my $update_notified_date=db_select($dbh,"select update_notified_date from ipr_detail where ipr_id=$ipr_id");
  if ($to_update_other_ipr) {
    if (my_defined($update_notified_date)) {
      print qq{<font color="red"><b>This update was notifed to the submitter of the IPR that is being updated on $update_notified_date.</b></font><br><br>
};
    } else {
      print qq{
  <br> $form_header_post
  <center> 
    <input type="hidden" name="ipr_id" value="$ipr_id">
    <input type="hidden" name="command" value="do_notice_update">
    <input type="submit" name="notice_it" value="Notice the submitter of IPR that is being updated">
</form> 
};
    }
  }
  if ($to_update_other_ipr == 0 or my_defined($update_notified_date)) {
    print qq{
  <br>
$form_header_post
  <center>
  <table>
    <tr>
    <td>
    <input type="hidden" name="ipr_id" value="$ipr_id">
    <input type="hidden" name="command" value="do_post_it">
    <input type="submit" name="post_it" value="Post It">
    </td>
</form>
};
  }
  print qq{
$form_header_post
    <td>
    <input type="hidden" name="ipr_id" value="$ipr_id">
    <input type="hidden" name="command" value="do_delete">
    <input type="submit" name="do_delete" value="Delete">
    </td></tr>
  </table>
  </form>
</center>
};

}
else {
  my $func = "${command}(\$ipr_id,\$q)";
  eval($func);
}
print qq{
  <a href="/public/ipr_disclosure.cgi"><img src="/images/blue.gif" hspace="3" border="0">IPR Disclosure Page</a><br><br>
  <a href="ipr_admin.cgi"><img src="/images/blue.gif" hspace="3" border="0">IPR Admin Page</a><br><br>
                                                                                                                
  </body></html>
};
$dbh->disconnect();
exit;

sub ipr_detail_display() {
my $ipr_id = shift;
my ($old_ipr_url, $additional_old_title1, $additional_old_url1, $additional_old_title2, $additional_old_url2, $submitted_date,$comply) = db_select($dbh,"select old_ipr_url,additional_old_title1,additional_old_url1,additional_old_title2,additional_old_url2,submitted_date,comply from ipr_detail where ipr_id = $ipr_id");
my $selecttype = db_select($dbh,"select selecttype from ipr_detail where ipr_id = $ipr_id");
my $comply_statement = ($comply)?"":"<font color=\"red\">This IPR disclosure does not comply with the formal requirements of Section 6, \"IPR Disclosures,\" of RFC 3979, \"Intellectual Property Rights in IETF Technology.\"</font><br>" ;
my $type_display = ($selecttype == 1)?"YES":"NO";
my ($licensing_option,$lic_opt_a_sub,$lic_opt_b_sub,$lic_opt_c_sub,$lic_checkbox) = db_select($dbh,"select licensing_option,lic_opt_a_sub,lic_opt_b_sub,lic_opt_c_sub,lic_checkbox from ipr_detail where ipr_id = $ipr_id");
  $licensing_option = '0' unless (my_defined($licensing_option));
  my $licensing_option_text = "";
  if ($licensing_option == 1) {
    $licensing_option_text = "a) No License Required for Implementers.\n";
    $licensing_option_text .= "\tLicensing declaration is limited solely to standards-track IETF documents.\n" if ($lic_opt_a_sub == 1);
  } elsif ($licensing_option == 2) {
    $licensing_option_text = "b) Royalty-Free, Reasonable and Non-Discriminatory License to All Implementers.\n";
    $licensing_option_text .= "\tLicensing declaration is limited solely to standards-track IETF documents.\n" if ($lic_opt_b_sub == 1);
  } elsif ($licensing_option == 3) {
    $licensing_option_text = "c) Reasonable and Non-Discriminatory License to All Implementers with Possible Royalty/Fee.\n";
    $licensing_option_text .= "\tLicensing declaration is limited solely to standards-track IETF documents.\n" if ($lic_opt_c_sub == 1);
  } elsif ($licensing_option == 4) {
    $licensing_option_text = "d) Licensing Declaration to be Provided Later.\n";
  } elsif ($licensing_option == 5) {
    $licensing_option_text = "e) Unwilling to Commit to the Provisions.\n";
  } elsif ($licensing_option == 6) {
    $licensing_option_text = "f) See Text Box Below for Licensing Declaration.\n";
  }
  my $lic_checkbox_text = ($lic_checkbox)?format_comment_text("The individual submitting this template represents and warrants that all terms and conditions that must be satisfied for implementers of any covered IETF specification to obtain a license have been disclosed in this IPR disclosure statement."):"";
  $lic_checkbox_text = html_bracket($lic_checkbox_text);
my ($p_h_legal_name,$document_title,$rfc_number,$id_document_tag,$other_designations,$p_applications,$date_applied,$country,$p_notes,$disclouser_identify,$other_notes,$comments,$generic,$third_party,$selectowned) = db_select($dbh,"select p_h_legal_name,document_title,rfc_number,id_document_tag,other_designations,p_applications,date_applied,country,p_notes,disclouser_identify,other_notes,comments,generic,third_party,selectowned from ipr_detail where ipr_id = $ipr_id");
  $disclouser_identify = "" unless my_defined($disclouser_identify);
my $filename = db_select($dbh,"select filename from internet_drafts where id_document_tag = $id_document_tag");
$filename = "" unless ($filename);
my $contact_type = db_select($dbh,"select contact_type from ipr_contacts where ipr_id = $ipr_id");
my ($ph_name, $ph_title, $ph_department, $ph_telephone, $ph_fax, $ph_email, $ph_address1, $ph_address2) = db_select($dbh,"select name,title,department,telephone,fax,email,address1,address2 from ipr_contacts where ipr_id = $ipr_id and contact_type = 1");
my ($ietf_name, $ietf_title, $ietf_department, $ietf_telephone, $ietf_fax, $ietf_email, $ietf_address1, $ietf_address2) = db_select($dbh,"select name,title,department,telephone,fax,email,address1,address2 from ipr_contacts where ipr_id = $ipr_id and contact_type = 2");
my ($sub_name, $sub_title, $sub_department, $sub_telephone, $sub_fax, $sub_email, $sub_address1, $sub_address2) = db_select($dbh,"select name,title,department,telephone,fax,email,address1,address2 from ipr_contacts where ipr_id = $ipr_id and contact_type = 3");

$p_notes = indent_text($p_notes,0);
$document_title = indent_text($document_title,0);
$comments = format_comment_text($comments);
$comments = html_bracket($comments);
$other_notes = indent_text($other_notes,0);
my $img_num = 2;
my $header_text = qq{   This document is an IETF IPR Disclosure and Licensing Declaration 
   Template and is submitted to inform the IETF of a) patent or patent application information regarding
   the IETF document or contribution listed in Section IV, and b) an IPR Holder's intention with respect to the licensing of its necessary patent claims.
   No actual license is implied by submission of this template. 
   Please complete and submit a separate template for each IETF document or contribution to which the
   disclosed patent information relates.

};
  my $temp_name = "Specific IPR Disclosures";
  my $possible = "";
  my $first_hd = "I";
  my $second_hd = "II";
  my $third_hd = "III";
  my $forth_hd = "IV";
  my $fifth_hd = "V";
  my $sixth_hd = "VI";
  my $seventh_hd="VII";
  my $eighth_hd= "VIII";
  my $displaying_section = "I, II, and IV";
if ($generic) {
  $img_num = 3;
  $fifth_hd = "III";
  $sixth_hd="IV";
  $seventh_hd="V";
  $eighth_hd="VI";
  $header_text = qq{
 This document is an IETF IPR Patent Disclosure and Licensing Declaration 
   Template and is submitted to inform the IETF of a) patent or patent application information that is not related to a specific IETF document or contribution, and b) an IPR Holder's intention with respect to the licensing of its necessary patent claims.
   No actual license is implied by submission of this template. 

};
  $temp_name = "Generic IPR Disclosures";
  $displaying_section = "I and II";
}

#$forth_hd = "III" if (my_defined($old_ipr_url));
if ($third_party) {
  $img_num = 4;
  $third_hd = "II";
  $forth_hd = "III";
  $fifth_hd = "IV";
  $possible = "Possible ";
  $header_text = qq{
This form is used to let the IETF know about patent information regarding an IETF document or contribution when the person letting the IETF know about the patent has no relationship with the patent owners.<br>

Click <a href="./ipr.cgi"> here</a>
if you want to disclose information about patents or patent applications
where you do have a relationship to the patent owners or patent applicants.
};
  $temp_name = "Notification";
  $displaying_section = "I, II, and III";
}
  my $section_v_c = qq{
    <td bgcolor="EEEEE3" width="710">$font_color1<small> C. If an Internet-Draft or RFC includes multiple parts and it is not
   reasonably apparent which part of such Internet-Draft or RFC is alleged
   to be covered by the patent information disclosed in Section
   V(A) or V(B), it is helpful if the discloser identifies here the sections of
   the Internet-Draft or RFC that are alleged to be so
   covered.</small></font>  </td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<b><pre>$disclouser_identify</pre></b></font></td>
};
  if ($generic) {
    my $selectowned_val = ($selectowned)?"YES":"NO";
    $section_v_c = qq{
    <td bgcolor="EEEEE3" width="710">$font_color1<small> C. Does this disclosure apply to all IPR owned by the submitter?
   </small></font>  </td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small><b>$selectowned_val</b></small></font></td>
                                                                                             
};
  }

print qq{
  <blockquote>
  <table cellpadding=0 cellspacing=0 border=0>
  <tr><td width="700" align="center">
  <h3>$document_title
  </td></tr>
  </table>
  <hr width="100%">
};
  if (my_defined ($old_ipr_url)) {
    print qq{
    <font size="3"> This IPR disclosure was submitted by e-mail.<br>
    $comply_statement
    Sections $displaying_section of "The Patent Disclosure and Licensing Declaration Template for $temp_name" have been completed for this IPR disclosure. Additional information may be available in the original submission.<br>
     Click <a href="$old_ipr_url">here</a> to view the content of the original IPR disclosure.</font><br>
};
  } else {
    print qq{
    <font size="3"> Only those sections of the "Patent Disclosure and Licensing Declaration Template for $temp_name" where the submitter provided information are displayed.<br>
};
  }
  if (my_defined ($additional_old_title1)) {
    print qq{
     <font size="3"><a href="$additional_old_url1">$additional_old_title1</a></font><br>
};
  }
  if (my_defined ($additional_old_title2)) {
    print qq{
     <font size="3"><a href="$additional_old_url2">$additional_old_title2</a></font><br>
};
  }
  if (my_defined ($submitted_date)) {
    my $month = db_select($dbh,"select monthname('$submitted_date')");
    my $year = db_select($dbh,"select year('$submitted_date')");
    my $day = db_select($dbh,"select dayofmonth('$submitted_date')");
    my $submitted_date_ver = "$month $day, $year";
    print qq{
    <br>
    <font size="3"><strong>Submitted Date : $submitted_date_ver</strong></font>
};
  }
print qq|
  <br>
  <table border="1" cellpadding="4" cellspacing="0" width="710" style="{padding:5px;border-width:1px;border-style:solid;border-color:305076}">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong> I. ${possible}Patent Holder/Applicant ("Patent Holder")</strong></td></tr>
    <tr>
  <td bgcolor="EEEEE3">$font_color1<small>Legal Name :<b>&nbsp&nbsp&nbsp $p_h_legal_name</b></small></font></td></tr>
  </table>
  </blockquote>
|;
print qq|
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" width="710" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}">
    <tr>
    <td bgcolor="AAAAAA" colspan=2>$font_color2<strong>${second_hd}. Patent Holder's Contact for License Application </strong></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB" width="15%">$font_color1<small>Name :</small></font></td>
    <td bgcolor="EBEBEB">$font_color1<small><b>$ph_name</b></small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Title :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<small><b>$ph_title</b></small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Department :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<small><b>$ph_department</b></small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Address1 :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<small><b>$ph_address1</b></small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Address2 :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<small><b>$ph_address2</b></small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Telephone :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<small><b>$ph_telephone</b></small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Fax :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<small><b>$ph_fax</b></small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Email :</small></font></td>
    <td bgcolor="EBEBEB">$font_color1<small><b>$ph_email</b></small></font></td></tr>
  </table>
  </blockquote>
| unless ($third_party);
unless ($generic) {
  my @List_rfc = db_select_multiple($dbh,"select rfc_number from ipr_rfcs where ipr_id=$ipr_id");
  my $rfc_number = "";
  my $temp_title = "";
  for my $array_ref (@List_rfc) {
    my ($val) = @$array_ref;
    my $title = db_select($dbh,"select rfc_name from rfcs where rfc_number=$val");
    $temp_title .= "<li> $title <br>";
    $rfc_number .= "$val <br>";
  }
  unless (my_defined($rfc_number)) {
    $rfc_number = db_select($dbh,"select rfc_number from ipr_detail where ipr_id=$ipr_id");
    $temp_title = "$temp_title<li> " . db_select($dbh,"select rfc_name from rfcs where rfc_number=$rfc_number") if (my_defined($rfc_number));
  }
  my @List_id = db_select_multiple($dbh,"select id_document_tag from ipr_ids where ipr_id=$ipr_id");
  my $filename_set = "";
  for my $array_ref (@List_id) {
    my ($val) = @$array_ref;
    my ($title,$filename,$revision) = db_select($dbh,"select id_document_name,filename,revision from internet_drafts where id_document_tag=$val");
    $temp_title .= "<li> $title<br>";
    $filename_set .= "$filename-$revision.txt <br>"; 
  }
  unless (my_defined($filename_set)) {
    my $val = db_select($dbh,"select id_document_tag from ipr_detail where ipr_id=$ipr_id");
    if (my_defined($val)) {
      my ($title,$filename,$revision) = db_select($dbh,"select id_document_name,filename,revision from internet_drafts where id_document_tag=$val");
      $temp_title .= "<li> $title<br>";
      $filename_set .= "$filename-$revision.txt <br>";
    }
  }
  my $title_row = "";
  my $id_row = "";
  my $rfc_row = "";
  my $other_row = "";
  if (my_defined($temp_title)) {
    $title_row= qq{<tr bgcolor="EBEBEB">
    <td>Title :</td>
    <td><b>$temp_title</b></td></tr>
};
  }
  if (my_defined($filename_set)) {
    $id_row = qq{<tr bgcolor="EBEBEB"><td>ID Filename:</td>
<td><b>$filename_set</b></td>
</tr>
};
  }
  if (my_defined($rfc_number)) {
    $rfc_row = qq{<tr bgcolor="EBEBEB"><td>RFC Number:</td>
<td><b>$rfc_number</b></td></tr>
};
  }
  my $other_d = db_select($dbh,"select other_designations from ipr_detail where ipr_id=$ipr_id");
  if (my_defined($other_d)) {
    $other_row = qq{<tr bgcolor="EBEBEB"><td width="50%">Designations for Other Contributions:</td>
<td>$font_color1<b><small> $other_d</small></b></font></td></tr>
};
  }
  print qq{
  <blockquote>
  <table  border="0" cellpadding="4" cellspacing="0" width="710" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong>$third_hd. Contact Information for the IETF Participant Whose Personal
   Belief Triggered this Disclosure :</strong></font> </td></tr>
    <tr>
    <td bgcolor="EEEEE3" width="15%">$font_color1<small> Name :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$ietf_name</b></small></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Title :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$ietf_title</b></small></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Department :</small></font></td>
    <td bgcolor="EEEEE3"><small><b>$ietf_department</b></small></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Address1 :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$ietf_address1</b></small></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Address2 :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$ietf_address2</b></small></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Telephone :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$ietf_telephone</b></small></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Fax :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$ietf_fax</b></small></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Email :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$ietf_email</b></small></td></tr>
  </table>
  </blockquote>
} if (my_defined($ietf_name));
  print qq{
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" width="710" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}">
    <tr>
    <td bgcolor="AAAAAA" colspan="2">$font_color2<strong>$forth_hd. IETF Document or Other Contribution to Which this IPR Disclosure Relates </strong></font></td></tr>
$title_row
$rfc_row
$id_row
$other_row
  </table>
  </blockquote>
};
} # end of unless($generic)
unless (my_defined($old_ipr_url)) {
  print qq{
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" width="710" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong> $fifth_hd. Disclosure of Patent Information (i.e., patents or patent
   applications required to be disclosed by Section 6 of RFC 3979)</strong></font></td></tr>
    <td bgcolor="EEEEE3" colspan=2>$font_color1<small> A. For granted patents or published pending patent applications,
   please provide the following information:</small></font> </td></tr>
    <td bgcolor="EEEEE3">$font_color1<small>Patent, Serial, Publication, Registration, or Application/File number(s) :<b>$p_applications</b></small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small> Date(s) granted or applied for :<b>$date_applied</b></small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small> Country :<b> $country</b></small></font></td>
    <tr>
    <td bgcolor="EEEEE3" colspan=2>$font_color1 <small>Additional Notes : </small></font></td></tr>
    <tr>
    <td  bgcolor="EEEEE3" colspan=2><b><pre>$p_notes</pre></b></td></tr>

    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>B. Does your disclosure relate to an unpublished pending patent application? </small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small><b>$type_display</b></small></font></td></tr>
    <tr>
$section_v_c
    </tr>
  </table>
  </blockquote>
} if (my_defined($p_applications) or my_defined($p_notes));
  print qq|
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" width="710" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}">
    <tr>
    <td bgcolor="AAAAAA" colspan=2>$font_color2<strong>$sixth_hd. Licensing Declaration </strong></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small>
        The Patent Holder states that 
       its position with respect to licensing any patent claims contained in the
       patent(s) or patent application(s) disclosed above that would necessarily be infringed by
       implementation of the technology required by the relevant IETF specification ("Necessary Patent Claims"), 
       for the purpose of implementing such specification,
        is as follows(select one licensing declaration option only):
           </small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small><b>$licensing_option_text</b></small></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small>Licensing information, comments, notes, or URL for further information :</small></font></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<b><pre>$comments</pre><br>$lic_checkbox_text</b></font></td></tr>
  </table>
  </blockquote>
| unless ($third_party);
  print qq|
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" width="710" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong>$seventh_hd. Contact Information of Submitter of this Form (if different from
   IETF Participant in Section III above)</strong> </td></tr>
    <tr>
    <td bgcolor="EEEEE3" width="15%">$font_color1<small>Name :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$sub_name</b></small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Title :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$sub_title</b></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Department :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$sub_department</b></small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Address1 :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$sub_address1</b></small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Address2 :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$sub_address2</b></small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Telephone :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<small><b>$sub_telephone</b></small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Fax :
    <td bgcolor="EEEEE3">$font_color1<small><b>$sub_fax</small></font></td></b></small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Email :
    <td bgcolor="EEEEE3">$font_color1<small><b>$sub_email</small></font></td></b></small></font></td></tr>
  </table>
  </blockquote>
| if (my_defined($sub_name));
  print qq|
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" width="710" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}">
    <tr>
    <td bgcolor="AAAAAA" colspan=2>$font_color2<strong>$eighth_hd. Other Notes: </strong></font></td></tr>
    <tr>
    <td  bgcolor="DDDDDD"><b><pre>$other_notes</pre></b></td></tr>
  </table>
  </blockquote>
| if (my_defined($other_notes));
} # end of unless $old_ipr defined
#"

} 

sub do_notice_update {
  my $ipr_id=shift;
  my $updated_ipr_id=db_select($dbh,"select updated from ipr_updates where ipr_id=$ipr_id and processed=0");
  my ($to_email,$to_name) = db_select($dbh,"select email,name from ipr_contacts where ipr_id=$ipr_id and contact_type=3");
  ($to_email,$to_name) = db_select($dbh,"select email,name from ipr_contacts where ipr_id=$ipr_id and contact_type=2") unless my_defined($to_email);
  my ($ori_email,$ori_name) = db_select($dbh,"select email,name from ipr_contacts where ipr_id=$updated_ipr_id and contact_type=3");
  ($ori_email,$ori_name) = db_select($dbh,"select email,name from ipr_contacts where ipr_id=$updated_ipr_id and contact_type=2") unless my_defined($ori_email);
  my ($ori_document_title,$ori_submitted_date) = db_select($dbh,"select document_title,submitted_date from ipr_detail where ipr_id=$updated_ipr_id");
  print qq{
$form_header_post
<input type="hidden" name="command" value="do_send_update_notification">
<input type="hidden" name="ipr_id" value="$ipr_id"> 
<h4>Notification to the submitter of IPR that's being updated</h4>
<textarea name="notify_original_submitter" rows=25 cols=74>
To: $ori_email
From: IETF Secretariat <ietf-ipr\@ietf.org>
Subject: IPR update notification 
                                                                               
Dear $ori_name:

We have just received a request to update the IPR disclosure, 
$ori_document_title (https://datatracker.ietf.org/public/ipr_detail_show.cgi?ipr_id=$updated_ipr_id), 
which was submitted by you on $ori_submitted_date. The name and email 
address of the person who submitted the update to your IPR disclosure are:
$to_name, $to_email.

If the person who submitted the update to your IPR disclosure is *not*
authorized to do so, then please let us know by sending a message to
ietf-action\@ietf.org within the next seven days. Otherwise, we will post
the new IPR disclosure and mark it as an update to the IPR disclosure
that you submitted.

Thank you

IETF Secretariat

</textarea>
<br><br>
<input type="submit" value=" Send notifications NOW "> </form>
<br><br>
                                                                               
};

}

sub do_post_it {
  my $ipr_id = shift;
  my $updated_ipr_id=0;
  db_update($dbh,"update ipr_detail set status = 1 where ipr_id = $ipr_id");

  my $document_title = db_select($dbh,"select document_title from ipr_detail where ipr_id=$ipr_id");
  my @List_ipr_update = db_select_multiple($dbh,"select id,updated,status_to_be from ipr_updates where ipr_id=$ipr_id and processed=0");
  for my $array_ref (@List_ipr_update) {
    my ($id,$old_ipr_id,$new_status) = db_select($dbh,"select id,updated,status_to_be from ipr_updates where ipr_id=$ipr_id");   
    $updated_ipr_id=$old_ipr_id;
    my $ipr_title = db_select($dbh,"select document_title from ipr_detail where ipr_id=$old_ipr_id");
    $ipr_title2 = $ipr_title;
    $ipr_title2 =~ s/ \(\d\)$//;
    my $l_ipr_title2 = lc($ipr_title2);
    my $l_document_title = lc($document_title);
    if ($l_ipr_title2 eq $l_document_title) {
      my $document_title2 = db_quote("$document_title (%)");
      my $doc_number = db_select($dbh,"select count(ipr_id) from ipr_detail where document_title like $document_title2");
      unless ($doc_number) { #no same ipr title before - number the orginal ipr
        
        my $ipr_title_old = db_quote("$document_title (1)");
        my $ipr_title_new = db_quote("$document_title (2)");

        db_update($dbh,"update ipr_detail set document_title=$ipr_title_old where ipr_id=$old_ipr_id");
        db_update($dbh,"update ipr_detail set document_title=$ipr_title_new where ipr_id=$ipr_id");

      } else { #already numbered = don't touch the original numbering
        $doc_number++;
        my $ipr_title_new = db_quote("$document_title ($doc_number)");

        db_update($dbh,"update ipr_detail set document_title=$ipr_title_new where ipr_id=$ipr_id");

      }
    }

    db_update($dbh,"update ipr_detail set status=$new_status where ipr_id=$old_ipr_id");
    db_update($dbh,"update ipr_updates set processed=1 where id=$id");

  }
  my $is_generic=db_select($dbh,"select generic from ipr_detail where ipr_id=$ipr_id");
  my $notify_gen_ad=($is_generic)?get_notify_gen_ad_text($ipr_id):"";
  my $c_time = get_current_time();
  my $c_date = get_current_date();
  open LOG, ">>$LOG";
  print LOG "[$c_time, $c_date] IPR <$document_title:$ipr_id> has been posted by $user\n\n";
  close LOG;
  my $notify_submitter_text = get_notify_submitter_text($ipr_id,$updated_ipr_id);
  my $notify_document_relatives = "";
  my @List_ids = db_select_multiple($dbh,"select id_document_tag from ipr_ids where ipr_id=$ipr_id");
  for my $array_ref (@List_ids) {
    my ($id_document_tag) = @$array_ref;
    $notify_document_relatives .= get_document_relatives($ipr_id,$id_document_tag,1);
  }
  my @List_rfcs = db_select_multiple($dbh,"select rfc_number from ipr_rfcs where ipr_id=$ipr_id");
  for my $array_ref (@List_rfcs) {
    my ($rfc_number) = @$array_ref;
    $notify_document_relatives .= get_document_relatives($ipr_id,$rfc_number,0);
  }
  print qq{
$form_header_post
<input type="hidden" name="command" value="do_send_notifications">
<input type="hidden" name="ipr_id" value="$ipr_id">
<h4>Notification to Submitter(s)</h4>
<textarea name="notify_submitter" rows=25 cols=80>
$notify_submitter_text
</textarea>
<br><br>
$notify_document_relatives
$notify_gen_ad
<input type="submit" value=" Send notifications NOW ">
</form>
<br><br>
};
}

sub get_document_relatives {
  my $ipr_id=shift;
  my $tag=shift;
  my $is_id=shift;
  my $doc_info="";
  my $author_names = "";
  my $author_emails = "";
  my $cc_list = "";
  my $sqlStr_a="";
  if ($is_id) {
    my ($id_name,$filename,$group_acronym_id) = db_select($dbh,"select id_document_name,filename,group_acronym_id from internet_drafts where id_document_tag=$tag");
    $doc_info="Internet-Draft entitled \"$id_name\" ($filename)";
    $sqlStr_a="select person_or_org_tag from id_authors where id_document_tag=$tag";
    if ($group_acronym_id == 1027) { #Individual Submisstion I-D
      my $ad_id = db_select($dbh,"select job_owner from id_internal where id_document_tag=$tag and rfc_flag=0");
      if ($ad_id > 0) { # has shepherding AD in ID Tracker
         my $person_or_org_tag = db_select($dbh,"select person_or_org_tag from iesg_login where id=$ad_id");
         $cc_list = get_email($person_or_org_tag);
      } else { # does not have shepherding AD. AD of the GEN area will be cc'ed, or Area advisor of wg acronym that is placed in third segment of filename will be cc'ed.
        my @temp=split '-',$filename;
        my $third_seg=$temp[2];
        my $alt_ad_id=db_select($dbh,"select area_director_id from acronym a, groups_ietf b where acronym='$thrid_seg' and acronym_id=group_acronym_id and status_id=1");
        my $person_or_org_tag=($alt_ad_id)?$alt_ad_id:db_select($dbh,"select person_or_org_tag from area_directors where area_acronym_id=1008");
        $cc_list = get_email($person_or_org_tag);
      }
    } else { #WG submisstion I-D
      my $wg_status=db_select($dbh,"select status_id from groups_ietf where group_acronym_id=$group_acronym_id");
      if ($wg_status == 1) { #Active WG
        $cc_list = get_wg_email_list($group_acronym_id,1);
      } else { #Concluded WG
        $cc_list = get_wg_email_list($group_acronym_id,0);
      }
    }
  } else {
    my ($rfc_name,$group_acronym) = db_select($dbh,"select rfc_name,group_acronym from rfcs where rfc_number=$tag");
    $group_acronym = "none" unless my_defined($group_acronym);
    $doc_info = "RFC entitled \"$rfc_name\" (RFC$tag)";
    $sqlStr_a = "select person_or_org_tag from rfc_authors where rfc_number=$tag";
    my $group_acronym_id=db_select($dbh,"select acronym_id from acronym where acronym='$group_acronym'");
    if ($group_acronym_id == 1027 or $group_acronym_id == 0) { #Individual Submisstion I-D
        my $person_or_org_tag=db_select($dbh,"select person_or_org_tag from area_directors where area_acronym_id=1008");
        $cc_list = get_email($person_or_org_tag); 
    } else { #WG submisstion I-D
      my $wg_status=db_select($dbh,"select status_id from groups_ietf where group_acronym_id=$group_acronym_id");
      if ($wg_status == 1) { #Active WG
        $cc_list = get_wg_email_list($group_acronym_id,1);
      } else { #Concluded WG
        $cc_list = get_wg_email_list($group_acronym_id,0);
      }
    }

  }
  my @List_a = db_select_multiple($dbh,$sqlStr_a);
  for my $array_ref (@List_a) {
    my ($person_or_org_tag)=@$array_ref;
    $author_name = get_name($person_or_org_tag);
    $author_email = get_email($person_or_org_tag);
    $author_names .= "$author_name, ";
    $author_emails .= "$author_email,";
  }
  chop $author_names;
  chop $author_names;
  chop $author_emails;
  $cc_list .= ",ipr-announce\@ietf.org";
  my ($submitted_date,$ipr_title) = db_select($dbh,"select submitted_date,document_title from ipr_detail where ipr_id=$ipr_id");
  my $email_body = format_comment_text("An IPR disclosure that pertains to your $doc_info was submitted to the IETF Secretariat on $submitted_date and has been posted on the \"IETF Page of Intellectual Property Rights Disclosures\" (https://datatracker.ietf.org/ipr/$ipr_id/). The title of the IPR disclosure is \"$ipr_title.\"");
  return qq{
<h4>Notification for $doc_info</h4>
<textarea name="notify_$is_id$tag" rows=25 cols=80>
To: $author_emails
From: IETF Secretariat <ietf-ipr\@ietf.org>
Subject: IPR Disclosure: $ipr_title
Cc: $cc_list

Dear $author_names:

$email_body

The IETF Secretariat

</textarea>
<br><br>
};
}


sub get_notify_gen_ad_text {
  my $ipr_id=shift;
  my $person_or_org_tag=db_select($dbh,"select person_or_org_tag from area_directors where area_acronym_id=1008");
  my $gen_ad_name=get_name($person_or_org_tag);
  my $gen_ad_email=get_email($person_or_org_tag);
  my ($submitted_date,$ipr_title) = db_select($dbh,"select submitted_date,document_title from ipr_detail where ipr_id=$ipr_id");
  my $email_body=format_comment_text("A generic IPR disclosure was submitted to the IETF Secretariat on $submitted_date and has been posted on the \"IETF Page of Intellectual Property Rights Disclosures\" (https://datatracker.ietf.org/public/ipr_list.cgi).  The title of the IPR disclosure is \"$ipr_title.\"");
  print qq{
<h4>Generic IPR notification to GEN AD, $gen_ad_name</h4>
<textarea name="notify_gen_ad" rows=25 cols=80>
To: $gen_ad_email
From: IETF Secretariat <ietf-ipr\@ietf.org>
Subject: Posting of IPR Disclosure
Cc:

Dear $gen_ad_name:

$email_body

The IETF Secretariat
</textarea>
<br><br>
<br>
};

}

sub get_wg_email_list {
  my $group_acronym_id=shift;
  my $wg_status_id=shift;
  my $ret_val = "";
  my $area_acronym_id = db_select($dbh,"select area_acronym_id from area_group where group_acronym_id=$group_acronym_id");
  my @List = db_select_multiple($dbh,"select person_or_org_tag from area_directors where area_acronym_id=$area_acronym_id");
  for my $array_ref (@List) {
    my ($person_or_org_tag) = @$array_ref;
    my $email = get_email($person_or_org_tag);
    $ret_val .= "$email,";
  }

  if ($wg_status_id) {
#    my $area_adv_tag = db_select($dbh,"select person_or_org_tag from area_directors a, groups_ietf b where b.group_acronym_id=$group_acronym_id and b.area_director_id=a.id");
#    my $email = get_email($area_adv_tag);
#    $ret_val = "$email,";
  my $wg_email_list = db_select($dbh,"select email_address from groups_ietf where group_acronym_id=$group_acronym_id");
  $ret_val .= "$wg_email_list,";
    my @List = db_select_multiple($dbh,"select person_or_org_tag from g_chairs where group_acronym_id=$group_acronym_id");
    for my $array_ref (@List) {
      my ($person_or_org_tag) = @$array_ref;
      my $email = get_email($person_or_org_tag);
      $ret_val .= "$email,";
    }
###CHANGES 01/31/2011
# The portion ater this was commented to avoid WG notification if the WG is closed but uncommented the code as per 
# ams000872
###CHANGES BEGIN
  } else {
    my $area_acronym_id = db_select($dbh,"select area_acronym_id from area_group where group_acronym_id=$group_acronym_id");
    my @List = db_select_multiple($dbh,"select person_or_org_tag from area_directors where area_acronym_id=$area_acronym_id");
    for my $array_ref (@List) {
      my ($person_or_org_tag) = @$array_ref;
      my $email = get_email($person_or_org_tag);
      $ret_val .= "$email,";
    }
##CHANGES END
  }
  chop $ret_val;
  return $ret_val;
};
sub get_notify_submitter_text {
  my $ipr_id=shift;
  my $updated_ipr_id=shift;
  my ($to_email,$to_name) = db_select($dbh,"select email,name from ipr_contacts where ipr_id=$ipr_id and contact_type=3");
  ($to_email,$to_name) = db_select($dbh,"select email,name from ipr_contacts where ipr_id=$ipr_id and contact_type=2") unless my_defined($to_email);
  ($to_email,$to_name) = db_select($dbh,"select email,name from ipr_contacts where ipr_id=$ipr_id and contact_type=1") unless my_defined($to_email);
  $to_email = "UNKNOWN EMAIL - NEED ASSISTANCE HERE" unless my_defined($to_email);
  $to_name = "UNKNOWN NAME - NEED ASSISTANCE HERE" unless my_defined($to_name);
  my $ipr_title = db_select($dbh,"select document_title from ipr_detail where ipr_id=$ipr_id");
  my $email_body = format_comment_text("Your IPR disclosure entitled \"$ipr_title\" has been posted on the \"IETF Page of Intellectual Property Rights Disclosures\" (https://datatracker.ietf.org/public/ipr_list.cgi).");
  my $subject = "Posting of IPR Disclosure";
  my $cc_list = "";
  if ($updated_ipr_id > 0) {
    $subject = "Posting of Updated IPR Disclosure";
    my ($old_submitted_date,$old_title) = db_select($dbh,"select submitted_date,document_title from ipr_detail where ipr_id=$updated_ipr_id");
    $email_body = format_comment_text("Your IPR disclosure entitled \"$ipr_title\" has been posted on the \"IETF Page of Intellectual Property Rights Disclosures\" (https://datatracker.ietf.org/public/ipr_list.cgi).  Your IPR disclosure updates IPR disclosure ID #$updated_ipr_id, \"$old_title,\" which was posted on $old_submitted_date");
    my $email_cc = db_select($dbh,"select email from ipr_contacts where ipr_id=$updated_ipr_id and contact_type=3");
    $email_cc =  db_select($dbh,"select email from ipr_contacts where ipr_id=$updated_ipr_id and contact_type=2") unless my_defined($email_cc);
    $cc_list = "$email_cc, " unless ($to_email eq $email_cc);
    for (my $loop=0;$loop<10;$loop++) { #Search for updated IPRs in depth of 10
      $email_cc = db_select($dbh,"select email from ipr_contacts where ipr_id=$updated_ipr_id and contact_type=1");
      $cc_list .= "$email_cc, " unless ($to_email eq $email_cc or $cc_list =~ /$email_cc/);
      $updated_ipr_id = db_select($dbh,"select updated from ipr_updates where ipr_id=$updated_ipr_id");
      last unless $updated_ipr_id; 
    }
    $email_cc = db_select($dbh,"select email from ipr_contacts where ipr_id=$ipr_id and contact_type=1");
    $cc_list .= "$email_cc, " unless ($to_email eq $email_cc or $cc_list =~ /$email_cc/);
    $cc_list =~ s/0, //g;
    $cc_list =~ s/^, //g;
    chop($cc_list) if my_defined($cc_list);
    chop($cc_list) if my_defined($cc_list);
  }
  my $ret_txt = qq{To: $to_email
From: IETF Secretariat <ietf-ipr\@ietf.org>
Subject: $subject
Cc: $cc_list

Dear $to_name:

$email_body

The IETF Secretariat
};
  return $ret_txt;
}

sub do_send_update_notification {
  my $ipr_id=shift;
  my $q=shift;
  my $notify_original_submitter=$q->param("notify_original_submitter");
  unless ($devel_mode) {
    my $ret_val=send_notification($notify_original_submitter,$ipr_id) if my_defined($notify_original_submitter);
    if ($ret_val) {
      print "<h3>Notificaions have been sent out and recorded in the database</h3>\n";
    } else {
      print "<h3>Failed to send out the notification</h3>\n";
      return;
    }
  } else {
    print qq{<pre>
$notify_original_submitter

</pre>
};
  }

  db_update($dbh,"update ipr_detail set update_notified_date=current_date where ipr_id=$ipr_id");

}
sub do_send_notifications {
  my $ipr_id=shift;
  my $q=shift;
  foreach ($q->param) {
    if (/notify/) {
      my $notification = $q->param("$_");
      my $db_n = db_quote($notification);
      my $sqlStr = "insert into ipr_notifications (ipr_id,notification,date_sent,time_sent) values ($ipr_id,$db_n,current_date,current_time)";
      unless ($devel_mode) { 
        my $ret_val=send_notification($notification,$ipr_id) if my_defined($notification);  
        if ($ret_val) {

          db_update($dbh,$sqlStr);

          print "<h3>Notificaions have been sent out and recorded in the database</h3>\n";
        } else {
          print "<h3>Failed to send out the notification</h3>\n";
        }
      } else {

        db_update($dbh,$sqlStr);

        print qq{
<pre>
$notification
<br><br>
</pre>
};
      }
    }
  }
  print qq{
<h3><a href="ipr_admin.cgi">Back to admin list page</a><h3>
};
  
}



sub send_notification {
  my $text = shift;
  my $ipr_id=shift;
  open MAIL, "| /usr/lib/sendmail -t" or return 0;
  print MAIL <<END_OF_MESSAGE;
$text
END_OF_MESSAGE

  close MAIL or return 0;
  mail_log("IPR Admin Tool","IPR update notification ($ipr_id)","Original Submitter","IPR Admin Tool");
  return 1;
}

sub do_delete {
  my $ipr_id = shift;

  db_update($dbh,"update ipr_detail set status = 2 where ipr_id = $ipr_id");

  print qq{
  <h3><a href="ipr_admin.cgi">Back to admin list page</a><h3>
  };
  my $document_title = db_select($dbh,"select document_title from ipr_detail where ipr_id=$ipr_id");
  my $c_time = get_current_time();
  my $c_date = get_current_date();
  open LOG, ">>$LOG";
  print LOG "[$c_time, $c_date] IPR <$document_title:$ipr_id> has been deleted by $user\n\n";
  close LOG;
}

print qq{
  </body></html>
};

