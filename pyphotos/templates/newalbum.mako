<%inherit file="base.mako" />

<form action="/newalbum" method="POST">
<input type='text' name='albumname' />
visible: <input type='checkbox' name='visible' checked='true' />

<button action='submit'>Submit</button>
</form>
