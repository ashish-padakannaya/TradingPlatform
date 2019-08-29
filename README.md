# TradingPlatform
Install pip first to setup environment dependencies</h2>
<pre><code>sudo easy_install pip</code></pre>

install virtualenv to isolate dev environment
<pre><code>pip install virtualenv</code></pre>

Create a Virtual env to get started(NOTE: you need to run this only the first time)
<pre><code>cd ~
virtualenv env</code></pre>

Next, Clone the repository in the home directory,activate the virtual environment and install the dependencies
<pre><code>
source env/bin/activate
cd TradingPlatform
pip install -r requirements.txt</code></pre>

Use this command if the dependenices weren't picked up for installation
<pre><code>pip install --upgrade -r requirements.txt</code></pre>

To run the server in development mode
<pre><code>cd ~/TradingPlatform/djangobackend/
python manage.py migrate
python manage.py runserver
</code></pre>


