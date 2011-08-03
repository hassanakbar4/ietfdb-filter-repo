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
$program_name="ipr_admin.cgi";
$user_name = $ENV{REMOTE_USER};
$user_name = $q->param("user_name") unless my_defined($user_name);
print qq{Content-type: text/html

<html>
<head><title>IPR Adim Update Page $mode_text</title></head>
<body>
};

############################ Global Variables ####################
my $form_header = "<form action=\"ipr_admin_update.cgi\" method=\"post\">\n<input type=\"hidden\" name=\"user_name\" value=\"$user_name\">";
my $font_color1 = qq{<font color="000000" face="Arial" Size=3>};
my $font_color2 = qq{<font color="333366" face="Arial" Size=2>};
############################# Global Variables ######################
$LOG = "/home/mlee/LOGs/ipr_admin_activity.log";
my $command = $q->param("command");
my $ipr_id = $q->param("ipr_id");
unless (my_defined($command)) {
  ipr_update($ipr_id);
}
elsif ($command eq "do_update") {
  do_update($q);
}
#PRI Changes
elsif ($command eq "do_send_notifications") {
   do_send_notifications($q);  
}
#ENds
else {
  if ($command eq "do_post_it") {
  do_post_it($ipr_id);
  }
  elsif ($command eq "do_delete") {
  do_delete($q,$ipr_id);
  }
}
print qq{
  </body></html>
};
$dbh->disconnect();

sub ipr_update {
my $ipr_id = shift;
my ($p_h_legal_name,$document_title,$other_designations,$p_applications,$date_applied,$country,$p_notes,$disclouser_identify,$other_notes,$comments,$lic_opt_a_sub,$lic_opt_b_sub,$lic_opt_c_sub) = db_select($dbh,"select p_h_legal_name,document_title,other_designations,p_applications,date_applied,country,p_notes,disclouser_identify,other_notes,comments,lic_opt_a_sub,lic_opt_b_sub,lic_opt_c_sub from ipr_detail where ipr_id = $ipr_id");
my ($old_ipr_url, $additional_old_title1, $additional_old_url1, $additional_old_title2, $additional_old_url2, $submitted_date,$third_party,$generic,$comply,$selectowned) = db_select($dbh,"select old_ipr_url,additional_old_title1,additional_old_url1,additional_old_title2,additional_old_url2,submitted_date,third_party,generic,comply,selectowned from ipr_detail where ipr_id = $ipr_id");


my $old_addendum = $additional_old_title1;
my $old_addendum_text = $additional_old_url1;



my $rfc_number = "";
my $filename_set = "";
my @List_rfc = db_select_multiple($dbh,"select rfc_number from ipr_rfcs where ipr_id=$ipr_id");
my @List_id = db_select_multiple($dbh,"select id_document_tag,revision from ipr_ids where ipr_id=$ipr_id");
for my $array_ref (@List_rfc) {
  my ($val) = @$array_ref;
  $rfc_number .= "$val\n";
}
for my $array_ref (@List_id) {
  my ($val,$revision) = @$array_ref;
  my $filename = db_select($dbh,"select filename from internet_drafts where id_document_tag=$val");
  $filename_set .= "$filename";
  $filename_set .= "-$revision.txt" if my_defined($revision);
  $filename_set .= "\n";
}
my $lic_opt_a_checked = ($lic_opt_a_sub)?"checked":"";
my $lic_opt_b_checked = ($lic_opt_b_sub)?"checked":"";
my $lic_opt_c_checked = ($lic_opt_c_sub)?"checked":"";
my $selecttype = db_select($dbh,"select selecttype from ipr_detail where ipr_id = $ipr_id");
my $third_party_checked = numtocheck($third_party);
my $generic_checked = numtocheck($generic);
my $comply_yes_checked = ($comply==1)?"checked":"";
my $comply_no_checked = ($comply==0)?"checked":"";
my $comply_na_checked = ($comply==-1)?"checked":"";

my $yes_checked = "";
my $no_checked = "";
my $yes_checked_owned = ($selectowned)?"checked":"";
my $no_checked_owned = ($selectowned)?"":"checked";
if ($selecttype) {
  $yes_checked = "checked";
} else {
  $no_checked = "checked";
}
my $section_v_c = qq{
    <td bgcolor="EEEEE3" colspan=2 width="650">$font_color1<small> C. If an Internet-Draft or RFC includes multiple parts and it
is not
   reasonably apparent which part of such Internet-Draft or RFC is alleged
   to be covered by the patent information disclosed in Section
   V(A) or V(B), it is helpful if the discloser identifies here the sections of
   the Internet-Draft or RFC that are alleged to be so
   covered.</small></font>  </td></tr>
    <tr>
    <td bgcolor="EEEEE3" colspan=3>$font_color1<textarea name="disclouser_identify" rows=8 cols=80>$disclouser_identify</textarea></font></td>
};
if ($generic) {
  $section_v_c = qq{
    <td bgcolor="EEEEE3" colspan=2>$font_color1<small>C. Does this disclosure apply to all IPR owned by the submitter? </small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3" colspan=2>$font_color1<input type="radio" name="selectowned" value="1" $yes_checked_owned>Yes
    <input type="radio" name="selectowned" value="0" $no_checked_owned>No</font></td>
};
}
my $type_display = db_select($dbh,"select type_display from ipr_selecttype where selecttype = $selecttype");
my ($licensing_option,$lic_checkbox) = db_select($dbh,"select licensing_option,lic_checkbox from ipr_detail where ipr_id = $ipr_id");
my $val1_checked = "";
my $val2_checked = "";
my $val3_checked = "";
my $val4_checked = "";
my $val5_checked = "";
my $val6_checked = "";
my $eval_str = "\$val${licensing_option}_checked = \"checked\"";
eval($eval_str);
my $lic_checkbox_checked = numtocheck($lic_checkbox);
my $filename = db_select($dbh,"select filename from internet_drafts where id_document_tag = $id_document_tag");
$filename = "" unless ($filename);
my ($contact_type) = db_select($dbh,"select contact_type from ipr_contacts where ipr_id = $ipr_id");
my ($ph_name, $ph_title, $ph_department, $ph_telephone, $ph_fax, $ph_email, $ph_address1, $ph_address2) = db_select($dbh,"select name,title,department,telephone,fax,email,address1,address2 from ipr_contacts where ipr_id = $ipr_id and contact_type = 1");
my ($ietf_name, $ietf_title, $ietf_department, $ietf_telephone, $ietf_fax, $ietf_email, $ietf_address1, $ietf_address2) = db_select($dbh,"select name,title,department,telephone,fax,email,address1,address2 from ipr_contacts where ipr_id = $ipr_id and contact_type = 2");
my ($sub_name, $sub_title, $sub_department, $sub_telephone, $sub_fax, $sub_email, $sub_address1, $sub_address2) = db_select($dbh,"select name,title,department,telephone,fax,email,address1,address2 from ipr_contacts where ipr_id = $ipr_id and contact_type = 3");
my $comply_info = qq{
  <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="#EBEBEB">$font_color1<strong><b>Complies with RFC 3979?</b></strong></td>
    <td bgcolor="#EBEBEB">
YES <input type="radio" name="comply" value="1" $comply_yes_checked><br>
NO <input type="radio" name="comply" value="0" $comply_no_checked><br>
N/A <input type="radio" name="comply" value="-1"$comply_na_checked><br>
</td></tr>
  </table>
};
my $status = db_select($dbh,"select status from ipr_detail where ipr_id=$ipr_id");
my $selected_1=""; 
my $selected_2=""; 
my $selected_3=""; 
eval("\$selected_$status=\"selected\"");
my $status_info = qq{
  <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="#EBEBEB">$font_color1<strong><b>IPR Status</b></strong></td>
    <td bgcolor="#EBEBEB"><select name="status">
<option value="1" $selected_1>Active</option>
<option value="2" $selected_2>Removed by Admin</option>
<option value="3" $selected_3>Removed by Request</option>
</select>
</td></tr>
  </table>
};
my ($old_ipr_id,$status_to_be) = db_select($dbh,"select updated,status_to_be from ipr_updates where ipr_id=$ipr_id");
my $rm_yes_check = ($status_to_be==3)?"checked":"";
my $rm_no_check = ($status_to_be==1)?"checked":"";
my $update_info = qq{
  <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="#EBEBEB">$font_color1<strong><b>IPR ID that is updated by this IPR: </b></strong></td>
    <td bgcolor="#EBEBEB"><input type="text" value="$old_ipr_id" name="updated">
</td></tr>
    <tr><td bgcolor="#EBEBEB">Remove old IPR?</td>
    <td bgcolor="#EBEBEB"><input type="radio" name="remove_old_ipr" value="1" $rm_yes_check> YES 
    <input type="radio" name="remove_old_ipr" value="0" $rm_no_check> NO</td></tr>
  </table>
};

print qq{
  $form_header
  <blockquote>
<h3>$document_title</h3>
};
    print qq{
    <table border="1" cellpadding="2" cellspacing="0" style="$STYLE_DEF">     <tr>
    <td bgcolor="EBEBEB">$font_color1 IPR Title :</td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="document_title" value="$document_title" size="80"></font></td></tr>   </blockquoe>
  </table>
    <table border="1" cellpadding="2" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1 <a href="$old_ipr_url" TARGET="_blank">Old IPR URL</a> :</td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="old_ipr_url" value="$old_ipr_url" size="80"></font></td></tr>
  </blockquoe>
  </table>
  <table border="1" cellpadding="2" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1 IPR Note or Addendum :</td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="additional_old_title1" size="100" value="$additional_old_title1"></font></td></tr>
  </table>
  <table border="1" cellpadding="2" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1 URL for Note / Addendum Text :</td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="additional_old_url1" size="80" value="$additional_old_url1"></font></td></tr>
  </table>
  <table border="1" cellpadding="2" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1 Additional Old Titile2 :</td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="additional_old_title2" size="100" value="$additional_old_title2"></font></td></tr>
  </table>
                                                                                                                        
   <table border="1" cellpadding="2" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1 Additional Old URL2 :</td>    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="additional_old_url2" size="80" value="$additional_old_url2"></font></td></tr>
  </table>
  <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1<strong><b>Third Party Notification?</b></strong></td>
    <td bgcolor="EBEBEB"><input type="checkbox" name="third_party" $third_party_checked></font></td></tr>
  </table>
  <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1<strong><b>Generic IPR?</b></strong></td>
    <td bgcolor="EBEBEB"><input type="checkbox" name="generic" $generic_checked></font></td></tr>
  </table>
  $comply_info
  $status_info
  $update_info
  };
    print qq{
    <br>
     <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1<strong><b>Submitted Date :</b></strong></td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="submitted_date" value="$submitted_date" size="20"></font></td></tr>
  </table>
    };
print qq|
  <br>
  <table border="1" cellpadding="4" cellspacing="0" style="{padding:5px;border-width:1px;border-style:solid;border-color:305076}" width="710">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong> I. Patent Holder/Organization ("Patent Holder")</strong></td></tr>
    <tr>
  <td bgcolor="EEEEE3" width="15%">$font_color1<small>Legal Name :</small></font></td>
  <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="p_h_legal_name" value="$p_h_legal_name" size="40"></font></td></tr>
  </table>
  </blockquote>
<blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}" width="710">
    <tr>
    <td bgcolor="AAAAAA" colspan=2>$font_color2<strong>II. Patent Holder's Contact for License Application </strong></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB" width="15%">$font_color1<small>Name :</small></font></td>
    <td bgcolor="EBEBEB">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ph_name"  value="$ph_name" size="25"></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Title :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ph_title" value="$ph_title" size="80"></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Department :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ph_department" value="$ph_department" size="80"></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Address1 :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ph_address1" value="$ph_address1" size="80"></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Address2 :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ph_address2" value="$ph_address2" size="80"></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Telephone :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ph_telephone" value="$ph_telephone" size="25"></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Fax :</small></font></td>
    <td bgcolor="EBEBEB" align="left">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ph_fax" value="$ph_fax" size="25"></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Email :</small></font></td>
    <td bgcolor="EBEBEB">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ph_email" value="$ph_email" size="35"></font></td></tr>
  </table>
  </blockquote>
  <blockquote>
  <table  border="0" cellpadding="4" cellspacing="0" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}" width="710">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong>III. Contact Information for the IETF Participant Whose Personal
   Belief Triggered the Disclosure in this Template (Optional):</strong></font> </td></tr>
    <tr>
    <td bgcolor="EEEEE3" width="15%">$font_color1<small> Name :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1l<input type="text" onkeypress="return handleEnter(this, event)" name="ietf_name" value="$ietf_name" size="25"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Title :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ietf_title" value="$ietf_title" size="80"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Department :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ietf_department" value="$ietf_department" size="80"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Address1 :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ietf_address1" value="$ietf_address1" size="80"></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Address2 :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ietf_address2" value="$ietf_address2" size="80"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Telephone :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ietf_telephone" value="$ietf_telephone" size="25"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Fax :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ietf_fax" value="$ietf_fax" size="25"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Email :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="ietf_email" value="$ietf_email" size="35"></font></td></tr>
  </table>
  </blockquote>
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}" width="710">
    <tr>
    <td bgcolor="AAAAAA" colspan="2">$font_color2<strong>IV. IETF Document or Working Group Contribution to Which Patent Disclosure Relates </strong></font></td></tr>
    <td bgcolor="EBEBEB">$font_color1<small>RFC Number :</small></font></td>
    <td bgcolor="EBEBEB">$font_color1<textarea name="rfc_number" rows="3" cols="8">$rfc_number</textarea></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>I-D Tag :</small></font></td>
    <td bgcolor="EBEBEB">$font_color1<textarea name="filename" rows="3" cols="50">$filename_set</textarea></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Other Designations :</small></font></td>
    <td bgcolor="EBEBEB">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="other_designations" value="$other_designations" size="70"></font></td></tr>
  </table>
  </blockquote>
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}" width="710">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong> V. Disclosure of Patent Information (i.e., patents or patent
   applications required to be disclosed by Section 6 of RFC 3979)</strong></font></td></tr>
    <td bgcolor="EEEEE3" colspan=2>$font_color1<small> A. For granted patents or published pending patent applications,
   please provide the following information:</small></font> </td></tr>
    <td bgcolor="EEEEE3">$font_color1<small>Patent, Serial, Publication, Registration, or Application/File number(s) :</small></font></td>
    <td bgcolor="EEEEE3"><input type="text" onkeypress="return handleEnter(this, event)" name="p_applications" value="$p_applications" size="40"> </td></tr>
</tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small> Date(s) granted or applied for :</small></font></td>
    <td bgcolor="EEEEE3"> <input type="text" onkeypress="return handleEnter(this, event)" name="date_applied" value="$date_applied" size="25"></td></tr>
    <tr>
    <td bgcolor="E2DFD3">$font_color1<small> Country :</small></font></td>
    <td bgcolor="E2DFD3"> <input type="text" onkeypress="return handleEnter(this, event)" name="country" value="$country" size="25"></td></tr>
    <tr>
    <td bgcolor="E2DFD3" colspan=2>$font_color1 <small>Additional Notes : </small></font></td></tr>
    <tr>
    <td  bgcolor="E2DFD3" colspan=2><textarea name="p_notes" rows=4 cols=80>$p_notes</textarea></td></tr>
    <tr>
    <td bgcolor="EEEEE3" colspan=2>$font_color1<small>B. Does your disclosure relate to an unpublished pending patent application? </small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3" colspan=2>$font_color1<input type="radio" name="selecttype" value="1" $yes_checked>Yes
    <input type="radio" name="selecttype" value="0" $no_checked>No</font></td></tr>
    <tr>
$section_v_c
  </tr>
  </table>
  </blockquote>
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}" width="710">
    <tr>
    <td bgcolor="AAAAAA" colspan=2>$font_color2<strong>VI. Licensing Declaration </strong></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small>The Patent Holder states that 
       its position with respect to licensing any patent claims contained in the
       patent(s) or patent application(s) disclosed above that would necessarily be infringed by
       implementation of the technology required by the relevant IETF specification ("Necessary Patent Claims"),       for the purpose of implementing such specification,
        is as follows(select one licensing declaration option only):
         </small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>a) <input type="radio" name="licensing_option" value="1" $val1_checked> No License Required for Implementers.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="checkbox" name="lic_opt_a_sub" $lic_opt_a_checked> This licensing declaration is limited solely to standards-track IETF documents. </small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>b) <input type="radio" name="licensing_option" value="2" $val2_checked> Royalty-Free, Reasonable and Non-Discriminatory License to All Implementers.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="checkbox" name="lic_opt_b_sub" $lic_opt_b_checked> This licensing declaration is limited solely to standards-track IETF documents.</small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>c) <input type="radio" name="licensing_option" value="3" $val3_checked> Reasonable and Non-Discriminatory License to All Implementers with Possible Royalty/Fee.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="checkbox" name="lic_opt_c_sub" $lic_opt_c_checked> This licensing declaration is limited solely to standards-track IETF documents.</small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>d) <input type="radio" name="licensing_option" value="4" $val4_checked> Licensing Declaration to be Provided Later (implies a
      willingness to commit to the provisions of<br> &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp a), b), or c) above to all implementers; otherwise, the next option
     "Unwilling to Commit to the<br> &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp Provisions of a), b), or c) Above" - must be selected)</small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>e) <input type="radio" name="licensing_option" value="5" $val5_checked> Unwilling to Commit to the Provisions
      of a), b), or c) Above </small></font></td></tr>
</small></td></tr>
     <tr>
    <td bgcolor="EBEBEB">$font_color1<small>f ) <input type="radio" name="licensing_option" value="6" $val6_checked> See text box below for licensing declaration.</small></font></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small>Licensing information, comments, notes or URL for further information :</small></font></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<textarea name="comments"  rows=5 cols=80>$comments</textarea></font></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small><input type="checkbox" name="lic_checkbox"  $lic_checkbox_checked>The individual submitting this template represents and warrants that all terms and conditions that must be satisfied for implementers of any covered IETF specification to obtain a license have been disclosed in this IPR disclosure statement.</small></font></td></tr>
  </table>
  </blockquote>
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}" width="710">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong>VII. Contact Information of Submitter of this Form (if different from
   IETF Participant in Section III above)</strong> </td></tr>
    <tr>
    <td bgcolor="EEEEE3" width="15%">$font_color1<small>Name :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="sub_name" value="$sub_name" size="25"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Title :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="sub_title" value="$sub_title" size="80"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Department :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="sub_department" value="$sub_department" size="80"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Address1 :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="sub_address1" value="$sub_address1" size="80"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Address2 :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="sub_address2" value="$sub_address2" size="80"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Telephone :</small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="sub_telephone" value="$sub_telephone" size="25"></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Fax : </small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="sub_fax" value="$sub_fax" size="25"></font></td></b></small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Email : </small></font></td>
    <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="sub_email" value="$sub_email" size="35"></font></td></b></small></font></td></tr>
  </table>
  </blockquote>
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="{padding:2px;border-width:1px;border-style:solid;border-color:305076}" width="710">
    <tr>
    <td bgcolor="AAAAAA" colspan=2>$font_color2<strong>VIII. Other Notes: </strong></font></td></tr>
    <tr>
    <td  bgcolor="DDDDDD"><textarea name="other_notes" rows=8 cols=80>$other_notes</textarea></td></tr>
  </table>
  </blockquote>
<center>
<table><tr><td>
<input type="hidden" name="ipr_id" value="$ipr_id">
<input type="hidden" name="command" value="do_update">
<input type="hidden" name="old_addendum" value="$old_addendum">
<input type="hidden" name="old_addendum_text" value="$old_addendum_text">
<input type="submit" name="submit" value="Update IPR"></a>
</form>
</td>
</tr>  
</table>
  </form>
<br><br>
$form_header
    <input type="hidden" name="ipr_id" value="$ipr_id">
    <input type="hidden" name="command" value="do_delete">
    <input type="submit" name="by_admin" value="Remove by Admin">
    <input type="submit" name="by_request" value="Remove by Request">
</form>

</center>
<br><br>
  <hr>
  <a href="./ipr_admin.cgi"><img src="/images/blue.gif" hspace="3" border="0">IPR Admin page</a><br><br>

|;
}                                                                                                                                                             
sub do_update {
  my $q = shift;
  my $ipr_id = $q->param("ipr_id");
  my $id_document_tag = "NULL";
  my $old_ipr_url = $q->param("old_ipr_url");
  my $additional_old_title1 = $q->param("additional_old_title1");
  my $additional_old_url1 = $q->param("additional_old_url1");
  my $additional_old_title2 = $q->param("additional_old_title2");
  my $additional_old_url2 = $q->param("additional_old_url2");
  my $third_party = checktonum($q->param("third_party"));
  my $generic = checktonum($q->param("generic"));
  my $comply = (my_defined($q->param("comply")))?$q->param("comply"):-1;
  my $submitted_date = $q->param("submitted_date");
  my $status = $q->param("status");
  my $p_h_legal_name = $q->param("p_h_legal_name");
  my $document_title = $q->param("document_title");
  my $rfc_number = $q->param("rfc_number");
  my $filename = $q->param("filename");
  my $other_designations = $q->param("other_designations");
  my $p_applications = $q->param("p_applications");
  my $date_applied = $q->param("date_applied");
  my $country = $q->param("country");
  my $p_notes = $q->param("p_notes");
  my $selecttype = $q->param("selecttype");
  my $selectowned = $q->param("selectowned");
  my $disclouser_identify = $q->param("disclouser_identify");
  my $licensing_option = $q->param("licensing_option");
  my $lic_checkbox = checktonum($q->param("lic_checkbox"));
  my $comments = $q->param("comments");
  my $other_notes = $q->param("other_notes");
  my $contact_id = $q->param("contact_id");
  my $contact_type = $q->param("contact_type");
  my $ph_name = $q->param("ph_name");
  my $ph_title = $q->param("ph_title");
  my $ph_department = $q->param("ph_department");
  my $ph_telephone = $q->param("ph_telephone");
  my $ph_fax = $q->param("ph_fax");
  my $ph_email = $q->param("ph_email");
  my $ph_address1 = $q->param("ph_address1");
  my $ph_address2 = $q->param("ph_address2");
  my $ietf_name = $q->param("ietf_name");
  my $ietf_title = $q->param("ietf_title");
  my $ietf_department = $q->param("ietf_department");
  my $ietf_telephone = $q->param("ietf_telephone");
  my $ietf_fax = $q->param("ietf_fax");
  my $ietf_email = $q->param("ietf_email");
  my $ietf_address1 = $q->param("ietf_address1");
  my $ietf_address2 = $q->param("ietf_address2");
  my $sub_name = $q->param("sub_name");
  my $sub_title = $q->param("sub_title");
  my $sub_department = $q->param("sub_department");
  my $sub_telephone = $q->param("sub_telephone");
  my $ietf_fax = $q->param("ietf_fax");
  my $ietf_email = $q->param("ietf_email");
  my $ietf_address1 = $q->param("ietf_address1");
  my $ietf_address2 = $q->param("ietf_address2");
  my $sub_name = $q->param("sub_name");
  my $sub_title = $q->param("sub_title");
  my $sub_department = $q->param("sub_department");
  my $sub_telephone = $q->param("sub_telephone");
  my $sub_fax = $q->param("sub_fax");
  my $sub_email = $q->param("sub_email");
  my $sub_address1 = $q->param("sub_address1");
  my $sub_address2 = $q->param("sub_address2");
  my $updated = $q->param("updated");
  my $lic_opt_a_sub = (my_defined($q->param("lic_opt_a_sub")))?checktonum($q->param("lic_opt_a_sub")):0;
  my $lic_opt_b_sub = (my_defined($q->param("lic_opt_b_sub")))?checktonum($q->param("lic_opt_b_sub")):0;
  my $lic_opt_c_sub = (my_defined($q->param("lic_opt_c_sub")))?checktonum($q->param("lic_opt_c_sub")):0;
  my $error_message = "";
  my @rfc_temp;
  my @id_temp;
  my $old_addendum = $q->param("old_addendum");
  my $old_addendum_text = $q->param("old_addendum_text");



  db_update($dbh,"delete from ipr_ids where ipr_id=$ipr_id",$program_name,$user_name);
  db_update($dbh,"delete from ipr_rfcs where ipr_id=$ipr_id",$program_name,$user_name);


  if (my_defined($rfc_number)) {
    $rfc_number =~ s/RFC//g;
    @rfc_temp = split '\n',$rfc_number;
    for my $array_ref (@rfc_temp) {
      chomp($array_ref);
      $array_ref =~ s/\r//;
      $error_message .= "RFC $array_ref is not valid<br>\n" unless (db_select($dbh,"select count(*) from rfcs where rfc_number = $array_ref"));
    }
  }
  if (my_defined($filename)) {
    my @temp = split '\n',$filename;
    for my $array_ref (@temp) {
      chomp($array_ref);
      $_ = $array_ref;
      s/\r//;
      s/.txt$//;
      /(\S+)-(\d\d$)/;
      my $revision = $2;
      s/-\d\d$//;
      my $id_document_tag = db_select($dbh,"select id_document_tag from internet_drafts where filename = '$_'");
      $error_message .= "ID '$_' is not valid<br>\n" unless ($id_document_tag);
      push @id_temp,"$id_document_tag-$revision";
    }
  }
  if (my_defined($error_message)) {

   print $error_message;
   return 0;
  }
  if ($updated > 0) {
    my $remove_old_ipr = $q->param("remove_old_ipr");     
    my $status_to_be = ($remove_old_ipr)?3:1;
    my $exist = db_select($dbh,"select count(*) from ipr_updates where ipr_id=$ipr_id");

    if ($exist) {


      db_update($dbh,"update ipr_updates set updated=$updated,status_to_be=$status_to_be where ipr_id=$ipr_id");


    } else {

      db_update($dbh,"insert into ipr_updates (ipr_id,updated,status_to_be,processed) values ($ipr_id,$updated,$status_to_be,1)");

    }

    db_update($dbh,"update ipr_detail set status=$status_to_be where ipr_id=$updated");

 
  }


  db_update($dbh,"delete from ipr_updates where ipr_id=$ipr_id") if ($updated < 0);


  ($date_applied,$p_applications, $p_applications,$old_ipr_url,$additional_old_title1,$additional_old_url1,$additional_old_title2,$additional_old_url2, $submitted_date,$p_h_legal_name,$document_title,$disclouser_identify,$other_notes,$comments, $other_designations, $p_notes,$country) = db_quote($date_applied,$p_applications, $p_applications,$old_ipr_url,$additional_old_title1,$additional_old_url1,$additional_old_title2,$additional_old_url2,$submitted_date,$p_h_legal_name,$document_title,$disclouser_identify,$other_notes,$comments, $other_designations, $p_notes,$country);
  $selecttype = '2' unless (my_defined($selecttype));
  $selectowned = '2' unless (my_defined($selectowned));
  $licensing_option = '0' unless (my_defined($licensing_option));
  my $sqlStr = "update ipr_detail set old_ipr_url=$old_ipr_url, additional_old_title1=$additional_old_title1, additional_old_url1=$additional_old_url1, additional_old_title2=$additional_old_title2, additional_old_url2=$additional_old_url2, submitted_date=$submitted_date, status=$status, p_h_legal_name=$p_h_legal_name, document_title=$document_title, other_designations=$other_designations, p_applications=$p_applications, date_applied=$date_applied, country=$country, p_notes=$p_notes, selecttype=$selecttype,selectowned=$selectowned, disclouser_identify=$disclouser_identify, licensing_option=$licensing_option, other_notes=$other_notes,comments=$comments,third_party=$third_party,generic=$generic,comply=$comply, lic_opt_a_sub=$lic_opt_a_sub,lic_opt_b_sub=$lic_opt_b_sub,lic_opt_c_sub=$lic_opt_c_sub,lic_checkbox=$lic_checkbox where ipr_id=$ipr_id";



  db_update($dbh,$sqlStr,$program_name,$user_name);

  if (my_defined($rfc_number)) {


    db_update($dbh,"delete from ipr_rfcs where ipr_id=$ipr_id",$program_name,$user_name);

    for my $array_ref (@rfc_temp) {
      chomp($array_ref);


      db_update($dbh,"insert into ipr_rfcs (ipr_id,rfc_number) values ($ipr_id,$array_ref)",$program_name,$user_name);

    }

    db_update($dbh,"update ipr_detail set rfc_number=null where ipr_id=$ipr_id",$program_name,$user_name);

  }
  if (my_defined($filename)) {


    db_update($dbh,"delete from ipr_ids where ipr_id=$ipr_id",$program_name,$user_name);

    for my $array_ref (@id_temp) {
      chomp($array_ref);
      my @temp=split '-',$array_ref;
      my $id_document_tag=$temp[0];
      my $revision=$temp[1];


      db_update($dbh,"insert into ipr_ids (ipr_id,id_document_tag,revision) values ($ipr_id,$id_document_tag,'$revision')",$program_name,$user_name);

    }


    db_update($dbh,"update ipr_detail set id_document_tag=null where ipr_id=$ipr_id",$program_name,$user_name);

  }

  ($ph_name,$ph_address1,$ph_address2,$ph_title,$ph_department) = db_quote($ph_name,$ph_address1,$ph_address2,$ph_title,$ph_department);
  my $new_ipr_contacts = "update ipr_contacts set ipr_id=$ipr_id, name=$ph_name, title=$ph_title, department=$ph_department, telephone='$ph_telephone', fax='$ph_fax', email='$ph_email', address1=$ph_address1, address2=$ph_address2 where ipr_id=$ipr_id and contact_type=1";
  $new_ipr_contacts = "insert into ipr_contacts (ipr_id,contact_type,name,title,department,telephone,fax,email,address1,address2) values ($ipr_id,1,$ph_name,$ph_title,$ph_department,'$ph_telephone','$ph_fax','$ph_email',$ph_address1,$ph_address2)" unless (db_select($dbh,"select count(*) from ipr_contacts where ipr_id=$ipr_id and contact_type=1"));


  db_update($dbh,$new_ipr_contacts,$program_name,$user_name);



    my ($ietf_name,$ietf_address1,$ietf_address2,$ietf_title,$ietf_department) = db_quote($ietf_name,$ietf_address1,$ietf_address2,$ietf_title,$ietf_department);
    my $new_ipr_contacts = "update ipr_contacts set ipr_id=$ipr_id, name=$ietf_name, title=$ietf_title, department=$ietf_department, telephone='$ietf_telephone', fax='$ietf_fax', email='$ietf_email', address1=$ietf_address1, address2=$ietf_address2 where ipr_id=$ipr_id and contact_type=2";
  $new_ipr_contacts = "insert into ipr_contacts (ipr_id,contact_type,name,title,department,telephone,fax,email,address1,address2) values ($ipr_id,2,$ietf_name,$ietf_title,$ietf_department,'$ietf_telephone','$ietf_fax','$ietf_email',$ietf_address1,$ietf_address2)" unless (db_select($dbh,"select count(*) from ipr_contacts where ipr_id=$ipr_id and contact_type=2"));


    db_update($dbh,$new_ipr_contacts,$program_name,$user_name);




    my ($sub_name,$sub_address1,$sub_address2,$sub_title,$sub_department) = db_quote($sub_name,$sub_address1,$sub_address2,$sub_title,$sub_department);
    my $new_ipr_contacts = qq{update ipr_contacts set ipr_id=$ipr_id, name=$sub_name, title=$sub_title, department=$sub_department, telephone='$sub_telephone', fax='$sub_fax', email='$sub_email', address1=$sub_address1, address2=$sub_address2 where ipr_id=$ipr_id and contact_type=3};
  $new_ipr_contacts = "insert into ipr_contacts (ipr_id,contact_type,name,title,department,telephone,fax,email,address1,address2) values ($ipr_id,3,$sub_name,$sub_title,$sub_department,'$sub_telephone','$sub_fax','$sub_email',$sub_address1,$sub_address2)" unless (db_select($dbh,"select count(*) from ipr_contacts where ipr_id=$ipr_id and contact_type=3"));


    db_update($dbh,$new_ipr_contacts,$program_name,$user_name);






my $new_title_length = length($additional_old_title1);
my $old_title_length = length($old_addendum);
my $new_url_length = length($additional_old_url1);
my $old_url_length = length($old_addendum_text);



$additional_old_title = rm_tr($additional_old_title);

 if (($third_party == 1) and (($new_title_length > 2 ) or ($new_url_length > 2))){


       do_post_it($ipr_id,$updated);

 }
 else{ 

   ipr_update($ipr_id);
  }
 
  
}


sub do_delete {
  my $q=shift;
  my $ipr_id = shift;
  my $status = (defined($q->param("by_request")))?3:2;

  db_update($dbh,"update ipr_detail set status = $status where ipr_id = $ipr_id",$program_name,$user_name);

  print qq{
  <h3><a href="ipr_admin.cgi">Back to admin list page</a><h3>
  };
  my $document_title = db_select($dbh,"select document_title from ipr_detail where ipr_id=$ipr_id");
  my $c_time = get_current_time();
  my $c_date = get_current_date();
  open LOG, ">>$LOG";
  print LOG "[$c_time, $c_date] IPR <$document_title:$ipr_id> has been deleted by $user\n\n";  close;
}     


#******************************************************#
#* WG-Notification and IPR - Notification additions   *#
#*****************************************************#
#


sub do_post_it {
  my $ipr_id = shift;
  my $updated_ipr_id = shift;
  my $c_time = get_current_time();
  my $c_date = get_current_date();
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
$form_header
<input type="hidden" name="command" value="do_send_notifications">
<input type="hidden" name="ipr_id" value="$ipr_id">
<h4> Notification to the submitter of IPR that's being updated</h4>
<h4> Please change the DATE and UPDATE NAME<h4>

<textarea name="notify_submitter" rows=25 cols=80>
$notify_submitter_text
</textarea>
<br><br>
$notify_document_relatives
$notify_wg
<input type="submit" value=" Send notifications NOW ">
</form>
<br><br>

};
}


sub get_notify_submitter_text {
  my $ipr_id=shift;
  my $updated_ipr_id=shift;
  my ($to_email,$to_name) = db_select($dbh,"select email,name from ipr_contacts where ipr_id=$ipr_id and contact_type=3");
  ($to_email,$to_name) = db_select($dbh,"select email,name from ipr_contacts where ipr_id=$ipr_id and contact_type=2") unless my_defined($to_email);
  ($to_email,$to_name) = db_select($dbh,"select email,name from ipr_contacts where ipr_id=$ipr_id and contact_type=1") unless my_defined($to_email);
  $to_email = "UNKNOWN EMAIL - NEED ASSISTANCE HERE" unless my_defined($to_email);
  $to_name = "UNKNOWN NAME - NEED ASSISTANCE HERE" unless my_defined($to_name);
  my $ipr_title = db_select($dbh,"select document_title from ipr_detail where ipr_id=$ipr_id");
  my $cc_list = "";


   

    $subject = "IPR disclosure Update Notification";

    $email_body = format_comment_text("On DATE, UDPATE NAME submitted an update to your 3rd party disclosure -- entitled \"$ipr_title\". The update has been posted on the \"IETF Page of Intellectual Property Rights Disclosures\" (https://datatracker.ietf.org/ipr/$ipr_id/)");





  if ($updated_ipr_id > 0) {
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

#   $email_body = format_comment_text("There has been an update to the 3rd party disclosure that pertains to Internet-Draft entitled
#\"$ipr_title\". The update was submitted to the IETF Secretariat on DATE by UPDATE NAME. It has been posted on the \"IETF Page of Intellectual Property Rights Disclosures\" (https://datatracker.ietf.org/ipr/$ipr_id/)");




   $email_body= format_comment_text("There has been an update to the 3rd party disclosure that pertains to \"$ipr_title\". The update was submitted to the IETF Secretariat on DATE by UPDATE NAME. It has been posted on the \"IETF Page of Intellectual Property Rights Disclosures\" (https://datatracker.ietf.org/ipr/$ipr_id/)");




  return qq{
<h4>Notification for $doc_info</h4>
<textarea name="notify_$is_id$tag" rows=25 cols=80>
To: $author_emails
From: IETF Secretariat <ietf-ipr\@ietf.org>
Subject: Updated IPR Disclosure: $ipr_title
Cc: $cc_list

Dear $author_names:

$email_body

The IETF Secretariat

</textarea>
<br><br>
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
  my $wg_email_list = db_select($dbh,"select email_address from groups_ietf where group_acronym_id=$group_acronym_id");
  $ret_val .= "$wg_email_list,";
    my @List = db_select_multiple($dbh,"select person_or_org_tag from g_chairs where group_acronym_id=$group_acronym_id");
    for my $array_ref (@List) {
      my ($person_or_org_tag) = @$array_ref;
      my $email = get_email($person_or_org_tag);
      $ret_val .= "$email,";
    }
###CHANGES 02/02/2011
# CHANGES TO ADD WG NOTIFICATIONS FOR CLOSED WG as per  ams000872
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
}

sub do_send_notifications{
  my $q=shift;
  my $ipr_id=shift;

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

