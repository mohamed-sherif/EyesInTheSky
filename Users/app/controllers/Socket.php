<?php
class mySocket
{
	private $host = "localhost";
  private $port = 5555;
  private $socket;

	function __construct()
	{
		$this->socket = socket_create(AF_INET, SOCK_STREAM,0) or die("Could not create socket\n");
    socket_connect($this->socket , $this->host,$this->port ) ;
	}
	function send($path)
	{
		$type ="user";
		$output = $path;
		socket_write($this->socket, $type, strlen ($type)) or die("Could not write output\n");
		sleep(1);
		socket_write($this->socket, $output, strlen ($output)) or die("Could not write output\n");
	}
	function receive()
	{


        $input = socket_read($this->socket, 1024) or die("Could not write output\n");

		echo "ana hena :" .$input;

		echo "string2";

		// if(socket_recv ( $this->socket , $buf , 2045 , MSG_WAITALL ) === FALSE)
		// {
		//     $errorcode = socket_last_error();
		//     $errormsg = socket_strerror($errorcode);
		     
		//     die("Could not receive data: [$errorcode] $errormsg \n");
		// }
		 
		// //print the received message
		// echo $buf;

	}



	function close()
	{
      socket_close($this->socket) ;
	}
}
?>