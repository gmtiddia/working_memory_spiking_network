
/*
*  nestml_7ac411a2439d4564ab240be13a43cd07_module.cpp
*
*  This file is part of NEST.
*
*  Copyright (C) 2004 The NEST Initiative
*
*  NEST is free software: you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation, either version 2 of the License, or
*  (at your option) any later version.
*
*  NEST is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
*
*  2024-09-25 09:28:46.846605
*/

// Include from NEST
#include "nest_extension_interface.h"

// include headers with your own stuff



#include "new_stp_synapse_nestml.h"


class nestml_7ac411a2439d4564ab240be13a43cd07_module : public nest::NESTExtensionInterface
{
  public:
    nestml_7ac411a2439d4564ab240be13a43cd07_module() {}
    ~nestml_7ac411a2439d4564ab240be13a43cd07_module() {}

    void initialize() override;
};

nestml_7ac411a2439d4564ab240be13a43cd07_module nestml_7ac411a2439d4564ab240be13a43cd07_module_LTX_module;

void nestml_7ac411a2439d4564ab240be13a43cd07_module::initialize()
{
    // register synapses
    nest::register_new_stp_synapse_nestml( "new_stp_synapse_nestml" );
}
