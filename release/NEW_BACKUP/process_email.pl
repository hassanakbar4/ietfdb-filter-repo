#!/usr/local/bin/perl -w
use lib '/export/home/mlee/RELEASE';
use IETF_UTIL;
use IETF_DBUTIL;

$PATH = "/export/home/mlee/INCOMING";
$LOG_PATH = "/export/home/mlee/DEVEL";
$ARCHIVE_PATH = "/export/home/mlee/DEVEL";
$DEPLOY = 1;
$TEST = 2;
$MYSQL = 3;
$sep_line = "----------------------------------------------------------";
$_ = `pwd`;
if (/DEVEL/) {
   $DB_MODE = $TEST;
} else {
   $DB_MODE = $DEPLOY;
}


$CURRENT_DATE = "CURRENT_DATE"; # "TODAY" for Informix, "CURRENT_DATE" for MySQL
$CONVERT_SEED = 1; # To convert date format to fit into the current database engine

if ($DB_MODE == $TEST) { #development mode
     $ENV{"DBNAME"} = "ietf_test";
} else  {
     $ENV{"DBNAME"} = "ietf";
} 

$sig_error_message = qq{SYSTEM COULD NOT PROCESS YOUR REQUEST DUE TO:

      System could not identify your signature

};

$mail_id = 0;
open ERROR_FILE,"$LOG_PATH/process.log";
while (<ERROR_FILE>) {
   @temp = split ':';
   $mail_id = $temp[0];
}
close ERROR_FILE;
if (my_defined($mail_id)) {
   $mail_id++;
} else {
   $mail_id = 1;
}

$template_str = qq {
##Just Select one command below##
$sep_line
command: template search info add update help
$sep_line
Search/Add/Update Criteria

filename: 
state: 
intended status: 
due date: 
responsible: 
assigned to: 
area acronym: 
group acronym: 
comment:  
$sep_line
};

$usage_str = qq {
The body of your email should have following format:(copy and paste the contents between dotted line)

$template_str

All the identifier field (word before ':') should be lower case and spelled out exactly described above.
You will receive a report from system by email whether your request has been
successful or not.

command options:
	help - your will receive this system usage text by emai
	search - If you don't specify any criteria, you will receive entire list
	info - you must include 'filename' identifier and its value and
	       you will receive its information by email
	update - you must include 'filename' identifier and at least one field 
		 that you want to update.
    add - you must include 'filename' identifier. The default values of each fields are:
		  state - Pre AD Evaluation
		  intended status - none
		  assigned to - email sender
		  
filename - draft filename
states -
	You must indicate one of following values with exact spelling and case.
	
	Pre AD Evaluation                                 
	AD Evaluation
	Expert Review                                     
	New Version Needed (WG/Author)                    
	Reading List                                      
	Last Call Requested                               
	Last Call Issued                                  
	Wait for Writeup                                  
	Wait for Last Call to End                         
	Ready for Telechat                                
	Defer
	Evaluation: Discuss                               
	Discuss Writing Received                          
	Token\@wg or Author                                
	New Version Coming                                
	Approved But Comments Needed                      
	Approved                                          
	Info to be sent                                   
	Info sent                                         
	RFC Ed Queue                                      
	RFC Published                                     
	AD to write --Don't publish                       
	Info to be sent                                   
	Info sent                                         
	AD re-review                                      
	Requested                                         
	Request Rejected                                  
	Discuss fix received                              
	Discuss Cleared, Wait for approval                
	Dead
intended status - must be one of following:

	BCP                      
	Draft Standard           
	Experimental             
	Historic                 
	Informational            
	Proposed Standard        
	Standard                 
	None                     
	Request                  
due date - The date format should be either 'YYYY-MM-DD' or 'MM/DD/YYYY'
responsible - responsible field text
assigned to - AD's first name
comment - comment

};

########################################
#      Main routine begins here
########################################
open OUTFILE, ">/export/home/mlee/INCOMING/incoming.txt";

while (<STDIN>) {
   print OUTFILE "$_";
}

close (OUTFILE);

my ($sender_email,$sender_subject) = get_sender_email();

generate_error_log("Sender's email could not be found") unless my_defined($sender_email);

send_msg($sender_email,$sig_error_message,0,$sender_subject) unless (check_signature()); 

my ($return_code,$return_msg) = process_request();
send_msg($sender_email,$return_msg,$return_code,$sender_subject);

exit();

########################################
#     End of main routine
########################################

###################################
# Function: process_request
# Parameter: none
# return:
#   $return_code - value to indicate whether the process has been 
#      successful or not
#   $return_msg - message to be sent to requestor. this can contain the
#      data that's been requested.
#
#   This function does following:
#	1. open file '$PATH/signed.txt
#	2. parse the file and grep necessary fields which can be:
#		- command (help,info,update)
#		- filename.
#		- new state.
#		- new intended_status.
#		- new due date.
#		- new responsible.
#		- new job owner
#		- new comment
# 	3. Do the command
#	4. return return_code and message
###################################
sub process_request {
   my ($command,$filename,$new_state,$new_intended_status,$new_status_date,$new_responsible,$new_job_owner,$new_comment,$area_acronym,$group_acronym) = parse_email();
   my $ret_val = 1;
   my $ret_msg = "";
   my ($user_id,$user_fName) = get_user_info();
   my $error_msg = qq {
Your request has not been processed due to:
 
};
   $command = lc($command);
   $filename = lc($filename);
   if ($command eq "help") {
      $ret_msg = $usage_str;
   } elsif ($command eq "info") {
      unless (my_defined($filename)) {
         $ret_val = 0;
	 $error_msg .= "\t'filename' NOT found\n";
      } else {
	 ($ret_val,$ret_msg) = process_info($user_id,$filename);
	 $error_msg .= $ret_msg unless ($ret_val);
      }
   } elsif ($command eq "update") {
      unless (my_defined($filename)) {
	 $ret_val = 0;
	 $error_msg .= "\t'filename' NOT found\n";
      } else {
	 ($ret_val,$ret_msg) = process_update($filename,$new_state,$new_intended_status,$new_status_date,$new_responsible,$new_job_owner,$new_comment,$user_id,$user_fName);
	 $error_msg .= $ret_msg unless ($ret_val);
      }
   } elsif ($command eq "search") {
      ($ret_val,$ret_msg) = process_search($filename,$new_state,$new_intended_status,$new_status_date,$new_responsible,$new_job_owner,$area_acronym,$group_acronym);
      $error_msg .= $ret_msg unless ($ret_val);
   
   } elsif ($command eq "add") {
	 ($ret_val,$ret_msg) = process_add($filename,$new_state,$new_intended_status,$new_status_date,$new_responsible,$new_job_owner,$new_comment,$user_id,$user_fName);
      $error_msg .= $ret_msg unless ($ret_val);
   
   } elsif ($command eq "template") {
       $ret_msg = $template_str;
   } else {
      $ret_val = 0;
      $error_msg .= "\t'command' can't be found or unknown.\n";
   }
   $ret_msg = $error_msg . $usage_str unless ($ret_val);
   return $ret_val,$ret_msg;
}

###################################
# Function: process_add
# Paramter:
#
# return
#   $ret_val - 1: Successful, 0: Failure
#   $ret_msg - message to requestor, either requested info or error message
#   This function processes the 'update' command by updating data from
#   the database
###################################
sub process_add {
   my ($filename,$new_state,$new_intended_status,$new_status_date,$new_responsible,$new_job_owner,$new_comment,$user_id,$user_name) = @_;
   my $ret_val = 1;
   my $ret_msg = "";
   my $group_flag = 12;
   my $cur_state_id = 10;
   my $rfc_flag = 0;
   my $new_job_owner_id = $user_id;
   $new_responsible = db_quote($new_responsible);
   my $ballot_id = db_select("select max(ballot_id) from id_internal");
   $ballot_id++;
   my $primary_flag = 1;
   my $token_name = db_quote($user_name);
   $sqlStr = qq {
   select email_address from email_addresses e,iesg_login i
   where i.id = $user_id
   AND i.person_or_org_tag = e.person_or_org_tag
   AND e.email_priority = 1
   };
   my $token_email = db_quote(rm_tr(db_select($sqlStr)));
   $filename = db_quote($filename);
   my $id_document_tag = db_select("select id_document_tag from internet_drafts where filename = $filename");
   unless ($id_document_tag) {
      $ret_val = 0;
      $ret_msg = "\tFile $filename NOT found from database\n";
   } else {
      my $duplicate = db_select("select count(*) from id_internal where id_document_tag = $id_document_tag");
	  if ($duplicate) {
	     $ret_val = 0;
		 $ret_msg = "\tThis file is already existed in draftTracker database\n";
	  }
   }
   if (my_defined($new_state)) {
      my $new_state_str = $new_state;
      $new_state = db_quote($new_state);
      $cur_state_id = db_select("select document_state_id from ref_doc_states where document_state_val = $new_state");
      unless ($cur_state_id) {
	 $ret_val = 0;
	 $ret_msg .= "\tUnknown document state $new_state\n";
      }
   }
   if (my_defined($new_status_date)) {
      $new_status_date = convert_date($new_status_date,$CONVERT_SEED)
   }
   $new_status_date = db_quote($new_status_date);
   if (my_defined($new_job_owner)) {
      $new_job_owner = db_quote($new_job_owner);
      $new_job_owner_id = db_select("select id from iesg_login where first_name = $new_job_owner");
      unless ($new_job_owner_id) {
         $ret_val = 0;
	     $ret_msg .= "\tUnknown AD's first name $new_job_owner\n";
      }
   }
   if (my_defined($new_comment)) {
      $new_comment = format_comment($new_comment);
      add_comment($new_comment,$id_document_tag,$user_id,$cur_state_id,$cur_state_id) if ($ret_val != 0);
   }
   if ($ret_val == 1) {
      $sqlStr = qq {
      insert into id_internal
      (id_document_tag,rfc_flag,group_flag,cur_state,prev_state,assigned_to,status_date,event_date,mark_by,job_owner,ref_history,ballot_id,primary_flag,token_name,email_display,token_email)
      values ($id_document_tag,$rfc_flag,$group_flag,$cur_state_id,$cur_state_id,$new_responsible,$new_status_date,$CURRENT_DATE,$user_id,$new_job_owner_id,999999,$ballot_id,$primary_flag,$token_name,$token_name,$token_email)
      };
      db_update($sqlStr);
      $ret_msg = "Adding is successful\n";
	  #$ret_msg .= $sqlStr;
   } else {
      $ret_msg .= "Adding is failure\n";
   }

   return $ret_val,$ret_msg;
}





###################################
# Function: process_update
# Paramter:
#
# return
#   $ret_val - 1: Successful, 0: Failure
#   $ret_msg - message to requestor, either requested info or error message
#   This function processes the 'update' command by updating data from
#   the database
###################################
sub process_update {
   my ($filename,$new_state,$new_intended_status,$new_status_date,$new_responsible,$new_job_owner,$new_comment,$user_id,$user_name) = @_;
   my $ret_val = 1;
   my $ret_msg = "";
   my $update_str = "";
   my $sqlStr_is = "";
   my $update_state = 0;
   my $state_comment = "";
   my $state_id;
   my $old_state_id;
   my $updated_fields = "";
   $filename = db_quote($filename);
   my $id_document_tag = db_select("select a.id_document_tag from internet_drafts a, id_internal b where filename = $filename and a.id_document_tag = b.id_document_tag");
   unless ($id_document_tag) {
      $ret_val = 0;
      $ret_msg = "\tFile $filename NOT found from database\n";
   }
   if (my_defined($new_state)) {
      my $new_state_str = $new_state;
      $new_state = db_quote($new_state);
      $state_id = db_select("select document_state_id from ref_doc_states where document_state_val = $new_state");
      unless ($state_id) {
	 $ret_val = 0;
	 $ret_msg .= "\tUnknown document state $new_state\n";
      } else {
	 $old_state_id = db_select("select cur_state from id_internal where id_document_tag = $id_document_tag");
	 $update_state = 1;
	 my $old_state = db_select("select document_state_val from ref_doc_states where document_state_id = $old_state_id");
         $state_comment = "State Changes to $new_state_str from $old_state by $user_name (email update)";
	 $updated_fields .= "state ";
	 $update_str .= qq {cur_state = $state_id,
prev_state = $old_state_id,
};
      }
   }
   if (my_defined($new_intended_status)) { # update internet_drafts table here
      $new_intended_status = db_quote($new_intended_status);
      my $intended_status_id = db_select("select intended_status_id from id_intended_status where status_value = $new_intended_status");
      unless ($intended_status_id) {
	 $ret_val = 0;
	 $ret_msg .= "\tUnknown intended status $new_intended_status\n";
      } else {
	 $sqlStr_is = qq {
	 update internet_drafts set intended_status_id = $intended_status_id
	 where id_document_tag = $id_document_tag
	 };
	 $updated_fields .= "intended status ";
      }
   }
   if (my_defined($new_job_owner)) {
      $new_job_owner = db_quote($new_job_owner);
      my $new_job_owner_id = db_select("select id from iesg_login where first_name = $new_job_owner");
      unless ($new_job_owner_id) {
         $ret_val = 0;
	 $ret_msg .= "\tUnknown AD's first name $new_job_owner\n";
      } else {
         $update_str .= "job_owner = $new_job_owner_id,\n";
	 $updated_fields .= "assigned to ";
      }
   }
   if (my_defined($new_status_date)) {
      $new_status_date = db_quote(convert_date($new_status_date,$CONVERT_SEED));
      $update_str .= "status_date = $new_status_date,\n";
      $updated_fields .= "due date ";
   }
   if (my_defined($new_responsible)) {
      $new_responsible = db_quote($new_responsible);
      $update_str .= "assigned_to = $new_responsible,\n";
      $updated_fields .= "responsible ";
   }
   if (my_defined($new_comment)) {
      $new_comment = format_comment($new_comment);
      my ($cur_state_id,$prev_state_id) = db_select("select cur_state,prev_state from id_internal where id_document_tag = $id_document_tag");
      add_comment($new_comment,$id_document_tag,$user_id,$cur_state_id,$prev_state_id) if ($ret_val != 0);
      $updated_fields .= "comment ";
   } 
   unless (my_defined($updated_fields)) {
      $ret_msg .= "No updating field specified\n";
	  $ret_val = 0;
   }
   my $sqlStr = qq {
update id_internal
set 
$update_str
mark_by = $user_id,
event_date = $CURRENT_DATE
where id_document_tag = $id_document_tag 
};
   if ($ret_val == 1) {
      db_update($sqlStr);
      add_comment($state_comment,$id_document_tag,$user_id,$state_id,$old_state_id) if (my_defined($state_comment));
      db_update($sqlStr_is) if (my_defined($sqlStr_is));
      $ret_msg = "Updating $updated_fields is successful\n";
   } else {
      $ret_msg .= "Updating database failed\n";
   }

   return $ret_val,$ret_msg;
}


###################################
# Function: add_comment
# Parameter:
#   $comment - text body of comment
#   $id_document_tag - Whom this comment belongs to
#   $user_id = Who creates this comment
# result: none
###################################
sub add_comment {
   my $comment=shift;
   my $id_document_tag = shift;
   my $user_id = shift;
   my $cur_state = shift;
   my $prev_state = shift;
   $comment = db_quote($comment);
   my $cur_time = db_quote(get_current_time());
   my $version = db_quote(db_select("select revision from internet_drafts where id_document_tag = $id_document_tag"));
   $sqlStr = qq {
   insert into document_comments
   (document_id,public_flag,comment_date,comment_time,version,comment_text,created_by,result_state,origin_state)
   values ($id_document_tag,0,$CURRENT_DATE,$cur_time,$version,$comment,$user_id,$cur_state,$prev_state)
   };
   db_update($sqlStr);
   return;
}

###################################
# Function: process_search
# Paramter:
#
# return
#   $ret_val - 1: Successful, 0: Failure
#   $ret_msg - message to requestor, either requested info or error message
#   This function processes the 'update' command by updating data from
#   the database
###################################
sub process_search {
   my ($filename,$state,$intended_status,$status_date,$responsible,$job_owner,$area_acronym,$group_acronym) = @_;
   my $ret_val = 1;
   my $ret_msg = "";
   my $error_msg = "";
   
   my $sqlStr = qq{
   select id.id_document_tag,id.filename, id.revision, state.status_date,state.event_date,state.job_owner,
   r1.document_state_val,state.assigned_to,state.rfc_flag,state.ballot_id,state.cur_state,id.intended_status_id
   from id_internal state, internet_drafts id, ref_doc_states r1};
   my $where_clause = qq {
   where id.id_document_tag = state.id_document_tag
   AND state.cur_state = r1.document_state_id
   AND state.rfc_flag = 0
   };
   
   if (my_defined($filename)) {
      $filename = "%${filename}%";
      $filename = db_quote($filename);
      $where_clause .= "AND id.filename like $filename\n";
   }
   if (my_defined($area_acronym)) {
      $area_acronym = db_quote($area_acronym);
      my $area_acronym_id = db_select("select acronym_id from acronym where acronym = $area_acronym");
      unless ($area_acronym_id) {
         $ret_val = 0;
         $error_msg .= "Unknown Area Acronym $area_acronym\n";
      }
      $sqlStr .= ", area_group";
      $where_clause .= qq {AND area_group.area_acronym_id = $area_acronym_id
      AND area_group.group_acronym_id = id.group_acronym_id
      };
   }
   if (my_defined($group_acronym)) {
      $group_acronym = db_quote($group_acronym);
      my $group_acronym_id = db_select("select acronym_id from acronym where acronym = $group_acronym");
      unless ($group_acronym_id) {
         $ret_val = 0;
         $error_msg .= "Unknown Group Acronym $group_acronym\n";
      }
      $where_clause .= "AND id.group_acronym_id = $group_acronym_id\n";
   }
   if (my_defined($state)) {      
      $state = db_quote($state);
      my $cur_state .= db_select("select document_state_id from ref_doc_states where document_state_val = $state");
      unless ($cur_state) {
         $ret_val = 0;
         $error_msg .= "Unknown state $state\n";
      }
      $where_clause .= "AND state.cur_state = $cur_state\n";
   }
   if (my_defined($job_owner)) {
       my @temp = split ' ',$job_owner;
       my $first_name = db_quote($temp[0]);
       my $job_owner_id = db_select("select id from iesg_login where first_name = $first_name or last_name = $first_name");
       unless ($job_owner_id) {
          $ret_val = 0;
          $error_msg .= "Unknown AD name $first_name\n";
       }
       $where_clause .= "AND state.job_owner = $job_owner_id\n";
   }
   if (my_defined($intended_status)) {
      $intended_status = db_quote($intended_status);
      my $intended_status_id = db_select("select intended_status_id from id_intended_status where status_value = $intended_status");
      unless ($intended_status_id) {
         $ret_val = 0;
         $error_msg .= "Unknown Intended status $intended_status\n";
      }
      $where_clause .= "AND id.intended_status_id = $intended_status_id\n";
   }
   if (my_defined($responsible)) {
      $responsible = db_quote($responsible);
      $where_clause = "AND assigned_to = $responsible\n";
   }
   if ($ret_val == 1) {
      $sqlStr .= $where_clause;
      $sqlStr .= "\n order by state.cur_state, state.ballot_id\n";
      $ret_msg = display_list($sqlStr);
   } else {
      $ret_msg = $error_msg;
      $ret_msg .= "Searching database failed\n";
   }

   return $ret_val,$ret_msg;
}

sub display_list {
   my $sqlStr = shift;
   my $list_txt = "search result\n$sep_line\n\n";
   $list_txt .= "File Name(Intended Status), State, Version, Due Date, Assigned To, Last Modified Date\n";
   $list_txt .= "$sep_line\n";
   my @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      my ($temp1,$filename,$revision,$status_date,$event_date,$job_owner,$cur_state,$temp2,$temp3,$temp4,$temp5,$intended_status_id) = rm_tr(@$array_ref);
      my $intended_status = rm_tr(db_select("select status_value from id_intended_status where intended_status_id = $intended_status_id"));
      $status_date = convert_date($status_date,1);
      $event_date = convert_date($event_date,1);
      my $job_owner_str = get_mark_by($job_owner);

      $list_txt .= "$filename($intended_status), $cur_state, $revision, $status_date, $job_owner_str, $event_date\n";
   }
   return $list_txt;
}

###################################
# Function: process_info
# Parameter:
#   $user_id = user's id in iesg_login table
#   $filename = filename
# return 
#   $ret_val - 1: Successful, 0: Failure
#   $ret_msg - message to requestor, either requested info or error message
# 
#   This function processes the 'info' command by pulling data from
#   the database
###################################
sub process_info {
   my $user_id = shift;
   my $filename = shift;
   my $filename2 = $filename;
   $filename = db_quote($filename);
   my $sqlStr = qq {
select a.id_document_tag,a.status_date,b.document_state_val,a.job_owner,d.status_value,
e.revision,a.assigned_to
from id_internal a,ref_doc_states b,id_intended_status d,
internet_drafts e   
where e.filename = $filename 
and a.id_document_tag = e.id_document_tag
and e.intended_status_id = d.intended_status_id
and a.cur_state = b.document_state_id
};
   my ($id_document_tag,$status_date,$cur_state_val,$job_owner,$intended_status,$revision,$responsible) = rm_tr(db_select($sqlStr));
   unless (my_defined($job_owner)) {
      return 0,"\tFile $filename not found from database\n";
   } else {
      $status_date = convert_date($status_date,1);
      my $comment_log = qq {
Comment Log

Date        Version   Comment
$sep_line---------------------
};
      $sqlStr = qq{
   select comment_date,version,comment_text,created_by from document_comments
   where document_id = $id_document_tag
   order by 1 desc
};
      my @commentList = db_select_multiple($sqlStr);
      for $array_ref (@commentList) {
         my ($comment_date,$version,$comment_text,$created_by) = rm_tr(@$array_ref);
         $comment_text = format_comment($comment_text);
         $comment_date = convert_date($comment_date,1);
         $comment_log .= qq{
$comment_date $version $comment_text
};
      }
      if ($#commentList < 0) {
         $comment_log = "";
      }
      my $job_owner_str = get_mark_by($job_owner);
      my $ret_msg = qq {
<following line is for update the draft above>
command: update
$sep_line
filename: $filename2
intended status: $intended_status
state: $cur_state_val
due date: $status_date
responsible: $responsible
assigned To: $job_owner_str
comment: 
$comment_log

$sep_line
};
      return 1,$ret_msg;
   }
}
#############################################################
#
# Function : format_comment
# Parameters:
#   $comment: text of comment
# return : HTML text of comment
#
# This function convert raw format text to HTML format text
#
############################################################
sub format_comment {
   my $comment = shift;
   $_ = $comment;
   #s/\s\s+/ /g; # Replace multiple spaces to single space
   s/<b>//g;
   s/<\/b>//g;
   s/\r//g;
   s/</&lt;/g;
   s/>/&gt;/g;
   s/\n/<br>/g;
   $comment = $_;
   $comment = "<pre>" . $comment;
   $comment .= "</pre>";
 
   return $comment;
}

############################################################
#
# Function : get_mark_by
# Parameters:
#   $loginid - login id of current user
# return : string of first name and last name pulled from iesg_login table
#
############################################################
sub get_mark_by {
   my $loginid = shift;
   #return "test";
   my ($fName,$lName) = db_select("select first_name,last_name from iesg_login where id = $loginid");
   $fName = rm_tr($fName);
   $lName = rm_tr($lName);
   my $new_mark_by = "$fName $lName";
   return $new_mark_by;
}

###################################
# Function: get_user_info
# Parameter: none
# return: 
#   $user_id - user's login id of draftTracker
#   $user_fName = user's first name
# 
#   This funcions pulls id and first_name from iest_login table
###################################
sub get_user_info {
   open TEMP_FILE,"$PATH/temp.txt";
   my $line = <TEMP_FILE>;
   close TEMP_FILE;
   my @temp = split '<',$line;
   $line = $temp[1];
   @temp = split '@',$line;
   my $pgp_id = db_quote($temp[0]);
   my ($user_id,$user_fName) = db_select("select id,first_name from iesg_login where pgp_id = $pgp_id");
   return $user_id,$user_fName;

}

###################################
# Function: parse_email
# Parameter: none
# return:
#   $command - Command
#   $filename - Draft's file name
#   $new_state - Draft's new state
#   $new_intended_status = Draft's new intended status
#   $new_status_date = Draft's new due date
#   $new_responsible - New Responsible field
#   $new_job_owner - New job owner field
#   $new_comment - New comment
###################################
sub parse_email {
   my $command = "";
   my $filename = "";
   my $new_state = "";
   my $new_intended_status = "";
   my $new_status_date = "";
   my $new_responsible = "";
   my $new_job_owner = "";
   my $new_comment = "";
   my $area_acronym = "";
   my $group_acronym = "";
   
   open SIGNED_FILE, "$PATH/signed.txt";
   while (<SIGNED_FILE>) {
      $command = get_field($_) if (/command:/);
      $filename =get_field ($_) if (/filename:/);
      $new_state = get_field($_) if (/state:/);
      $new_intended_status = get_field($_) if (/intended status:/);
      $new_status_date = get_field($_) if (/due date:/);
      $new_responsible = get_field($_) if (/responsible:/);
      $new_job_owner = get_field($_) if (/assigned to:/);
      if (/comment:/) {
	  $new_comment = get_field($_) . "\n";
	  while (<SIGNED_FILE>) {
	     if ($_ eq $sep_line) {
		last;
             }
	     $new_comment .= $_;
	  }
	 last;
      }
      $new_comment = get_field($_,1) if (/comment:/);
      $area_acronym = get_field($_) if (/area acronym:/);
      $group_acronym = get_field($_) if (/group acronym:/);
   }
   close SIGNED_FILE;

   return ($command,$filename,$new_state,$new_intended_status,$new_status_date,$new_responsible,$new_job_owner,$new_comment,$area_acronym,$group_acronym);
}

###################################
# Function: get_field
# Parameter:
#    $line - a string of line to be parsed
# return: parsed value field
###################################
sub get_field {
   my $line = shift;
   my $comment_switch = shift;
   my @temp = split ':',$line;
   my $ret_val = $temp[1];
   $ret_val = rm_tr($ret_val);
   $ret_val = rm_hd($ret_val) unless (defined($comment_switch));
   return $ret_val;
}

###################################
# Function: check_signature
# Parameter: none
# return: 1 if valid signature
#         0 if invalid signature
#   This file executes system command 'pgp' to verify the signature file.
#   The actual command to execute is 'pgp $PATH/signed.txt.asc'
#   If 'signed.txt' is created, return 1, else return 0
###################################
sub check_signature {
   $ENV{"PGPPATH"} = "/export/home/mlee/.pgp";
   system "/usr/local/bin/pgp $PATH/signed.txt.asc > $PATH/temp.txt";
   if (-e "$PATH/signed.txt") {
      return 1;
   } else {
      return 0;
   } 
   return 0;
}
 
###################################
# Function: get_sender_email
# Parameter: none
# return: email address or null string
# Assumption: The body of message file should be ascii and NOT-encrypted
#    This function looks up 'From:' field from $PATH/incoming.txt,
#    parse out the email address, copy $PATH/incoming.txt to 
#    $PATH/signed.txt.asc and then returns the email address
#    If any problem occurs, return null string.
###################################
sub get_sender_email {
   my $email_line = "";
   my $subject_line = "";
   system "rm $PATH/signed*;cp $PATH/incoming.txt $PATH/signed.txt.asc";
   open S_INFILE, "$PATH/signed.txt.asc" or return "";
   while (<S_INFILE>) {
      if (/From:/) {
         $email_line = $_;
      }
      if (/Subject:/) {
         $subject_line = $_;
         last;
      }
   }
   return "","" unless my_defined($email_line);
   @temp = split '<',$email_line;
   $temp_val = $temp[1];
   @temp = split '>', $temp_val;
   my $email_address = $temp[0];
   @temp = split ':',$subject_line;
   my $subject = "Re: " . $temp[1];

   return $email_address,$subject;
}

###################################
# Function: send_msg
# Parameters:
#   $sender_email - email address of requestor
#   $msg - a message to be sent to the requestor
# return: none
#   This function sends a message to the requestor,
#   and then terminate the program
###################################
sub send_msg {
   my $sender_email = shift;
   my $msg = shift;
   my $return_code = shift;
   my $subject = shift;
   my $reply_email = "draft_tracker\@ietf.org";
   if ($DB_MODE == $TEST) {
      $sender_email = "mlee\@ietf.org";
   }
   open MAIL, "| /usr/lib/sendmail -t -i" or generate_error_log("Can't open sendmail",$sender_email);
   print MAIL <<END_OF_MESSAGE;
To: $sender_email
Cc: mlee\@ietf.org 
From: "DraftTracker Mail System" <draft_tracker\@ietf.org>
Reply-To: $reply_email
Subject: $subject -- MAIL ID [$mail_id]

$msg
END_OF_MESSAGE
   close MAIL or generate_error_log("Can't close sendmail",$sender_email);
   clean_up($return_code,$sender_email);
   exit();

}

 
###################################
# Function: clean_up
# Parameter:
#   $return_code - indicates whether the request proccess
#                  has been successfull or failure
# return: none
#    This function appends a message to either $PATH/process.log
#    or $PATH/process.log depends on the $return_code,
#    remove all temporary files, archive the original message,
#    and then remove the original message from processing directory.
###################################
sub clean_up {
   my $return_code = shift;
   my $email = shift;
   my $status = "Successful";
   $status = "Failed" unless ($return_code);
   open PROCESS_LOG, ">>$LOG_PATH/process.log";
   print PROCESS_LOG "$mail_id:$status:$email\n";
   close PROCESS_LOG;
   open ORIGINAL_FILE, "$PATH/signed.txt.asc";
   open ARCHIVE_FILE, ">>$ARCHIVE_PATH/all_mail.log";
   print ARCHIVE_FILE "Mail ID: [$mail_id]\n";
   while (<ORIGINAL_FILE>) {
      print ARCHIVE_FILE "$_";
   } 
   close ORIGINAL_FILE;
   close ARCHIVE_FILE;
   unlink "$PATH/signed.txt";
   unlink "$PATH/signed.txt.asc";
   unlink "$PATH/temp.txt";
   return ;
}
 
###################################
# Function: generate_error_log
# Parameters: 
#    $error_msg - Error message 
# return: none
#    This function appends error message to $LOG_PATH/process.log,
#    then terminate the program returning some value to sendmail
#    program so a sender can receive some sort of error message.
###################################
sub generate_error_log {
   my $error_msg = shift;
   my $email = shift;
   clean_up(0,"Unknown Email");
   open ERROR_LOG,">>$LOG_PATH/process.log" or exit(1);
   print ERROR_LOG "$mail_id:Failed:$email:$error_msg:\n"; 
   close ERROR_LOG;
   exit(1);
}
