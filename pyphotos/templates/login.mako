<%inherit file="base.mako" />

   <form action='/login' method='POST' name="formular">
      login: <input type="text" name="login" />
      password:  <input type="password" name="password" />

      <button action="submit" name="submit"> login! </button>
   </form>

   <form action="/login/openid" method="post">
         <input type="hidden" name="popup_mode" value="popup" />
         <input type="hidden" name="openid_identifier" value="https://www.google.com/accounts/o8/id" />
         <input type="submit" value="Login with Google" />
   </form> 

