<%inherit file="base.mako" />

<div>Please provide a username for ${request.user}</div>
<form method="post">
username:<input type="text" name="username"/>
<input type="submit" id='x' value='submit' />
</form>
