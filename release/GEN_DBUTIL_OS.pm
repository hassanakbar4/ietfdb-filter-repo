##########################################################################
# Copyright © 2004 and 2002, Foretec Seminars, Inc.
##########################################################################

package GEN_DBUTIL;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(get_dbh db_update db_select db_select_multiple init_database db_quote update_db_log db_error_log);

use lib '/a/www/ietf-datatracker/release/';
use DBI;
use GEN_UTIL;

sub db_error_log {
  my $program_name=shift;
  my $sqlStr = shift;
  my $user=shift;
  open IDLOG, ">>/a/www/ietf-datatracker/logs/db_error.log";
  my $c_date = get_current_date();
  my $c_time = get_current_time();
  print IDLOG qq{[$c_date, $c_time] $program_name 
SQL: $sqlStr
User: $user

};
  close IDLOG;
}

sub update_db_log {
  my $program_name=shift;
  my $sqlStr =shift;
  my $user=shift;
  my $c_time = get_current_time();
  my $c_date = get_current_date();
  open LOG, ">>/a/www/ietf-datatracker/logs/update_db.log";
  print LOG qq{[$c_time, $c_date] $program_name
SQL: $sqlStr
User: $user
                                                                                         
};
  close LOG;
}

sub init_database {
  my $dbname = shift;
  return 0 unless (my_defined($dbname));
  $ENV{"DBNAME"} = $dbname;
  return 1;
}

sub db_quote {
  my @list = @_;
  for ($loop=0;$loop<=$#list;$loop++) {
    $list[$loop] =~ s/'/''/g;
    $list[$loop] =~ s/\\/\\\\/g; 
    $list[$loop] = "'" . rm_tr($list[$loop]);
    $list[$loop] .= "'";
  }
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }
}
                                                                                                     

sub get_dbh {
   $dbname = $ENV{"DBNAME"};
   my $dbh;
   $dbh = DBI->connect("dbi:mysql:$dbname:localhost","ietf","ietfietf");
   #$dbh = DBI->connect("dbi:mysql:$dbname:localhost","mlee","sunnyohm");
   return $dbh;
}


sub db_update {
   my $sqlStr = shift;
   my $program_name=shift;
   my $user = shift;
   my $dbh = get_dbh();
   my $failed = 0;
   my $sth = $dbh->prepare($sqlStr) or $failed = 1;
   if ($failed) {
     db_error_log($program_name,$sqlStr,$user) if (defined($program_name) and defined($user));
     return 0;
   }
   $sth->execute() or $failed=1;
   if ($failed) {
     db_error_log($program_name,$sqlStr,$user) if (defined($program_name) and defined($user));
     return 0;
   }

   $dbh->disconnect();
   update_db_log($program_name,$sqlStr,$user) if (defined($program_name) and defined($user));
   return 1;
}

sub db_select {
   my $sqlStr = shift;
   my @list;
   my $dbh = get_dbh();
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute() or return 0;
   @list = $sth->fetchrow_array();
   #$dbh->disconnect();
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }
}

sub db_select_multiple {
   my $sqlStr = shift;
   my $dbh = get_dbh();
   my $sth = $dbh->prepare($sqlStr) or return 0;
   $sth->execute() or return 0;
   my @nList;
   while (my @row = $sth->fetchrow_array()) {
      push @nList, [ @row ];
   }
   return @nList;
}
