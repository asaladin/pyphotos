<%inherit file="base.mako" />

<h2>Admin Page</h2>

<h3>Import album from S3</h3>

<form method='post' action='/import/s3'>
albumname: <input type='text' name='albumname' /> <br />
directory: <input type='text' name='dirname' /> <br />
visible: <input type='checkbox' name='visible' checked='true' />
<button action='submit'>Submit</button>
</form>

<hr />


