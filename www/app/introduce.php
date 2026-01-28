<?php

//
// Controller for display
// https://{domain}/introduce/greeting
//
class Greeting extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(10);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make()
    {
        $this->module();
    }

    public function module()
    {
        $module = new \Module\Contents\Make_Controller();
        $module->set('key', 'greeting');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/introduce/introduction
//
class Introduction extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(11);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make()
    {
        $this->module();
    }

    public function module()
    {
        $module = new \Module\Contents\Make_Controller();
        $module->set('key', 'introduction');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/introduce/education
//
class Education extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(12);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make()
    {
        $this->module();
    }

    public function module()
    {
        $module = new \Module\Contents\Make_Controller();
        $module->set('key', 'education');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/introduce/contact
//
class Contact extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(13);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make()
    {
        $this->module();
    }

    public function module()
    {
        $module = new \Module\Contents\Make_Controller();
        $module->set('key', 'contact');
        $module->run();
    }

}
