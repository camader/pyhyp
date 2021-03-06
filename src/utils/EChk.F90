subroutine EChk(ierr, file, line)

  ! Check if ierr that resulted from a petsc or MPI call is in fact an
  ! error. 
  use precision
  use communication

  implicit none

#include "include/petscversion.h"
#if PETSC_VERSION_MINOR > 5
#include "petsc/finclude/petsc.h"
#else
#include "include/finclude/petsc.h"
#endif

  integer(kind=intType),intent(in) :: ierr
  character*(*),intent(in) :: file
  integer(kind=intType),intent(in) :: line

  if (ierr == 0) then
     return ! No error, return immediately
  else
     call MPI_Comm_rank(hyp_comm_world, myid, ierr)
     print *,'================================================================='
     write(*,900) "PETSc or MPI Error. Error Code ",ierr,". Detected on Proc ",myid
     write(*,901) "Error at line: ",line," in file: ",file
     print *,'================================================================='

     call MPI_Abort(hyp_comm_world,ierr)
     stop ! Just in case
  end if

900 format(A,I2,A,I2)
901 format(A,I5,A,A)
end subroutine EChk

