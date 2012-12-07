<html>
<head>
<title>Photos</title>

<style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
      .sidebar-nav {
        padding: 9px 0;
      }
    </style>



<link href="/static/bootstrap.css" rel="stylesheet">
<script src="static/bootstrap.js"></script>
</head>

<body>




    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
          <a class="brand" href="/">PyPhotos</a>
          <div class="nav-collapse">
            <ul class="nav">
              <li><a href="/">Home</a></li>
            ##  <li><a href="#about">About</a></li>
            ##  <li><a href="#contact">Contact</a></li>
            </ul>
            %if request.user is not None:
                <p class="navbar-text pull-right">Logged in as <a href="#">${request.username}</a> | <a href='/logout' id='signout'> logout </a> </p>
            %else: 
               <p class="navbar-text pull-right"><a href="/login">Log in </a></p> 
            %endif    
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>



<div class="container-fluid">

     <div class="flash"> 
        <% flash = request.session.pop_flash()   %>
        %for message in flash:
             ${message} <br />
        %endfor
     </div>

     <div class="row-fluid">

         <div class="span2">
             <div class="well sidebar-nav">
                 <ul class="nav nav-list">
                     <li class="nav-header">Sidebar</li>
    <!--             <li class="active"><a href="#">Link</a></li>-->
                    %if request.user is not None:
                     <li><a href='/newalbum'>Create an album</a></li>
                    %endif
                     <li class="nav-header">Your albums</li>
                     %for a in myalbums[:5]:
                         <li><a href="/album/${a['title']}/list">${a['title']}</a></li>
                     %endfor
                 </ul>
             </div><!--/.well -->
         </div><!--/span-->



         <div class='span9'>
             ${next.body()}
         </div>

<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
<script src="https://login.persona.org/include.js"></script>

<script type="text/javascript">

 $('#signin').click(function() { navigator.id.request(); return false;});

$('#signout').click(function() { navigator.id.logout(); return false;});

%if request.user is None:
var currentUser = null;
%else:
var currentUser = '${request.user}';
%endif
 
navigator.id.watch({
  loggedInUser: currentUser,
  onlogin: function(assertion) {
    // A user has logged in! Here you need to:
    // 1. Send the assertion to your backend for verification and to create a session.
    // 2. Update your UI.
    $.ajax({ /* <-- This example uses jQuery, but you can use whatever you'd like */
      type: 'POST',
      url: '/login/browserid', // This is a URL on your website.
      data: {assertion: assertion},
      success: function(res, status, xhr) { window.location.reload(); },
      error: function(xhr, status, err) { alert("Login failure: " + err); }
    });
  },
  onlogout: function() {
    // A user has logged out! Here you need to:
    // Tear down the user's session by redirecting the user or making a call to your backend.
    // Also, make sure loggedInUser will get set to null on the next page load.
    // (That's a literal JavaScript null. Not false, 0, or undefined. null.)
    $.ajax({
      type: 'POST',
      url: '/logout', // This is a URL on your website.
      success: function(res, status, xhr) { window.location.reload(); },
      error: function(xhr, status, err) { alert("Logout failure: " + err); }
    });
  }
});
</script>



</body>

</html>
