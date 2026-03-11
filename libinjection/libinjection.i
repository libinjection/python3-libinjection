/* libinjection.i SWIG interface file */
%module libinjection
%{
#include "libinjection.h"
#include "libinjection_sqli.h"
#include "libinjection_xss.h"
#include "libinjection_error.h"
#include <stddef.h>

/* This is the callback function that runs a python function
 *
 */
static char libinjection_python_check_fingerprint(sfilter* sf, int lookuptype, const char* word, size_t len)
{
    PyObject *fp;
    PyObject *arglist;
    PyObject *result;
    char ch;

    // get sfilter->pattern
    // convert to python string
    fp = SWIG_InternalNewPointerObj((void*)sf, SWIGTYPE_p_libinjection_sqli_state,0);

    arglist = Py_BuildValue("(Nis#)", fp, lookuptype, word, len);
    // call pyfunct with string arg
    result = PyObject_CallObject((PyObject*) sf->userdata, arglist);
    Py_DECREF(arglist);
    if (result == NULL) {
        // python call has an exception
        // pass it back
        ch = '\0';
    } else {
        // convert value of python call to a char (Python 3 compatible)
        if (PyUnicode_Check(result)) {
            Py_ssize_t size;
            const char* str = PyUnicode_AsUTF8AndSize(result, &size);
            ch = (str != NULL && size > 0) ? str[0] : '\0';
        } else if (PyBytes_Check(result)) {
            const char* str = PyBytes_AsString(result);
            ch = (str != NULL) ? str[0] : '\0';
        } else {
            ch = '\0';
        }
        Py_DECREF(result);
    }
    return ch;
}

%}
%include "typemaps.i"

// The C functions all start with 'libinjection_' as a namespace
// We don't need this since it's in the libinjection python package
// i.e. libinjection.libinjection_is_sqli --> libinjection.is_sqli
 //
%rename("%(strip:[libinjection_])s") "";

// SWIG doesn't natively support fixed sized arrays.
// this typemap converts the fixed size array sfilter.tokevec
// into a list of pointers to stoken_t types. In otherword this code makes this example work
// s = sfilter()
// libinjection_is_sqli(s, "a string",...)
// for i in len(s.pat):
//   print s.tokevec[i].val
//

%typemap(out) stoken_t [ANY] {
int i;
$result = PyList_New($1_dim0);
for (i = 0; i < $1_dim0; i++) {
    PyObject *o =  SWIG_NewPointerObj((void*)(& $1[i]), SWIGTYPE_p_stoken_t,0);
    PyList_SetItem($result,i,o);
}
}

// automatically append string length into arg array
%apply (char *STRING, size_t LENGTH) { (const char *s, size_t slen) };
%apply (char *STRING, size_t LENGTH) { (const char *s, size_t len) };

// Make the fingerprint output parameter in libinjection_sqli() work as an output
// The fingerprint buffer size matches libinjection's internal LIBINJECTION_SQLI_MAX_TOKENS (5) + null byte
#define LIBINJECTION_FINGERPRINT_SIZE 8
%typemap(in, numinputs=0) char fingerprint[] (char temp[LIBINJECTION_FINGERPRINT_SIZE]) {
    memset(temp, 0, sizeof(temp));
    $1 = temp;
}
%typemap(argout) char fingerprint[] {
    $result = SWIG_Python_AppendOutput($result, PyUnicode_FromString($1));
}

%typemap(in) (ptr_lookup_fn fn, void* userdata) {
    if ($input == Py_None) {
        $1 = NULL;
        $2 = NULL;
    } else {
        $1 = libinjection_python_check_fingerprint;
        $2 = $input;
    }
}
%include "libinjection_error.h"
%include "libinjection.h"
%include "libinjection_sqli.h"
%include "libinjection_xss.h"
