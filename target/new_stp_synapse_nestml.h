/**
 *  new_stp_synapse_nestml.h
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
 *  Generated from NESTML at time: 2024-09-25 10:54:28.751273
**/

#ifndef NEW_STP_SYNAPSE_NESTML_H
#define NEW_STP_SYNAPSE_NESTML_H

// C++ includes:
#include <cmath>

// Includes from nestkernel:
#include "common_synapse_properties.h"
#include "connection.h"
#include "connector_model.h"
#include "event.h"


// Includes from sli:
#include "dictdatum.h"
#include "dictutils.h"

/** @BeginDocumentation

**/

//#define DEBUG

namespace nest
{
// Register the synapse model
void register_new_stp_synapse_nestml( const std::string& name );

namespace new_stp_synapse_nestml_names
{
    const Name _u( "u" );
    const Name _x( "x" );
    const Name _t_ls( "t_ls" );
    const Name _w( "w" );
    const Name _U( "U" );
    const Name _tau_rec( "tau_rec" );
    const Name _tau_fac( "tau_fac" );
    const Name _delay( "delay" );
}

class new_stp_synapse_nestmlCommonSynapseProperties : public CommonSynapseProperties {
public:

    new_stp_synapse_nestmlCommonSynapseProperties()
    : CommonSynapseProperties()
    {
    }

    /**
     * Get all properties and put them into a dictionary.
     */
    void get_status( DictionaryDatum& d ) const
    {
        CommonSynapseProperties::get_status( d );
    }


    /**
     * Set properties from the values given in dictionary.
     */
    void set_status( const DictionaryDatum& d, ConnectorModel& cm )
    {
      CommonSynapseProperties::set_status( d, cm );
    }

    // N.B.: we define all parameters as public for easy reference conversion later on.
    // This may or may not benefit performance (TODO: compare with inline getters/setters)
};

template < typename targetidentifierT >
class new_stp_synapse_nestml : public Connection< targetidentifierT >
{
private:
  double t_lastspike_;

  /**
   * Dynamic state of the synapse.
   *
   * These are the state variables that are advanced in time by calls to
   * send(). In many models, some or all of them can be set by the user
   * through ``SetStatus()``.
   *
   * @note State_ need neither copy constructor nor @c operator=(), since
   *       all its members are copied properly by the default copy constructor
   *       and assignment operator. Important:
   *       - If State_ contained @c Time members, you need to define the
   *         assignment operator to recalibrate all members of type @c Time . You
   *         may also want to define the assignment operator.
   *       - If State_ contained members that cannot copy themselves, such
   *         as C-style arrays, you need to define the copy constructor and
   *         assignment operator to copy those members.
  **/
  struct State_{    
    double u;
    double x;
    double t_ls;

    State_() {};
  };

  /**
   * Free parameters of the synapse.
   *


   *
   * These are the parameters that can be set by the user through @c SetStatus.
   * Parameters do not change during calls to ``send()`` and are not reset by
   * @c ResetNetwork.
   *
   * @note Parameters_ need neither copy constructor nor @c operator=(), since
   *       all its members are copied properly by the default copy constructor
   *       and assignment operator. Important:
   *       - If Parameters_ contained @c Time members, you need to define the
   *         assignment operator to recalibrate all members of type @c Time . You
   *         may also want to define the assignment operator.
   *       - If Parameters_ contained members that cannot copy themselves, such
   *         as C-style arrays, you need to define the copy constructor and
   *         assignment operator to copy those members.
  */
  struct Parameters_{    
    double w;
    double U;
    double tau_rec;
    double tau_fac;



    /** Initialize parameters to their default values. */
    Parameters_() {};
  };

  /**
   * Internal variables of the synapse.
   *
   *
   * These variables must be initialized by recompute_internal_variables().
  **/
  struct Variables_
  {    
    double __h;
  };

  Parameters_ P_;  //!< Free parameters.
  State_      S_;  //!< Dynamic state.
  Variables_  V_;  //!< Internal Variables
  // -------------------------------------------------------------------------
  //   Getters/setters for parameters and state variables
  // -------------------------------------------------------------------------

  inline double get_u() const
  {
    return S_.u;
  }

  inline void set_u(const double __v)
  {
    S_.u = __v;
  }inline double get_x() const
  {
    return S_.x;
  }

  inline void set_x(const double __v)
  {
    S_.x = __v;
  }inline double get_t_ls() const
  {
    return S_.t_ls;
  }

  inline void set_t_ls(const double __v)
  {
    S_.t_ls = __v;
  }

  inline double get_w() const
  {
    return P_.w;
  }

  inline void set_w(const double __v)
  {
    set_weight(__v);
  }inline double get_U() const
  {
    return P_.U;
  }

  inline void set_U(const double __v)
  {
    P_.U = __v;
  }inline double get_tau_rec() const
  {
    return P_.tau_rec;
  }

  inline void set_tau_rec(const double __v)
  {
    P_.tau_rec = __v;
  }inline double get_tau_fac() const
  {
    return P_.tau_fac;
  }

  inline void set_tau_fac(const double __v)
  {
    P_.tau_fac = __v;
  }

  // -------------------------------------------------------------------------
  //   Getters/setters for inline expressions
  // -------------------------------------------------------------------------

  

  // -------------------------------------------------------------------------
  //   Function declarations
  // -------------------------------------------------------------------------



  /**
   * Update internal state (``S_``) of the synapse according to the dynamical equations defined in the model and the statements in the ``update`` block.
  **/
  inline void
  update_internal_state_(double t_start, double timestep, const new_stp_synapse_nestmlCommonSynapseProperties& cp);

  void recompute_internal_variables();

public:
  // this line determines which common properties to use
  typedef new_stp_synapse_nestmlCommonSynapseProperties CommonPropertiesType;

  typedef Connection< targetidentifierT > ConnectionBase;
  static constexpr ConnectionModelProperties properties = ConnectionModelProperties::HAS_DELAY
    | ConnectionModelProperties::IS_PRIMARY | ConnectionModelProperties::SUPPORTS_HPC
    | ConnectionModelProperties::SUPPORTS_LBL;

  /**
  * Default constructor.
  *
  * Sets default values for all parameters (skipping common properties).
  *
  * Needed by GenericConnectorModel.
  */
  new_stp_synapse_nestml();

  /**
  * Copy constructor from a property object.
  *
  * Sets default values for all parameters (skipping common properties).
  *
  * Needs to be defined properly in order for GenericConnector to work.
  */
  new_stp_synapse_nestml( const new_stp_synapse_nestml& rhs );

  // Explicitly declare all methods inherited from the dependent base
  // ConnectionBase. This avoids explicit name prefixes in all places these
  // functions are used. Since ConnectionBase depends on the template parameter,
  // they are not automatically found in the base class.
  using ConnectionBase::get_delay_steps;
  using ConnectionBase::set_delay_steps;
  using ConnectionBase::get_delay;
  using ConnectionBase::set_delay;
  using ConnectionBase::get_rport;
  using ConnectionBase::get_target;


  class ConnTestDummyNode : public ConnTestDummyNodeBase
  {
  public:
    // Ensure proper overriding of overloaded virtual functions.
    // Return values from functions are ignored.
    using ConnTestDummyNodeBase::handles_test_event;
    size_t
    handles_test_event( SpikeEvent&, size_t ) override
    {
      return invalid_port;
    }
    size_t
    handles_test_event( RateEvent&, size_t ) override
    {
      return invalid_port;    }
    size_t
    handles_test_event( DataLoggingRequest&, size_t ) override
    {
      return invalid_port;    }
    size_t
    handles_test_event( CurrentEvent&, size_t ) override
    {
      return invalid_port;    }
    size_t
    handles_test_event( ConductanceEvent&, size_t ) override
    {
      return invalid_port;    }
    size_t
    handles_test_event( DoubleDataEvent&, size_t ) override
    {
      return invalid_port;    }
    size_t
    handles_test_event( DSSpikeEvent&, size_t ) override
    {
      return invalid_port;    }
    size_t
    handles_test_event( DSCurrentEvent&, size_t ) override
    {
      return invalid_port;    }
  };

  /**
   *  special case for weights in NEST: only in case a NESTML state variable was specified in code generation options as ``weight_variable``
  **/
  inline void set_weight(double w)
  {
    P_.w = w;
  }
  /**
   *  special case for weights in NEST: only in case a NESTML state variable was specified in code generation options as ``weight_variable``
  **/
  inline double get_weight() const
  {
    return P_.w;
  }
  void
  check_connection( Node& s,
    Node& t,
    size_t receptor_type,
    const CommonPropertiesType& cp )
  {
    ConnTestDummyNode dummy_target;
    ConnectionBase::check_connection_( dummy_target, s, t, receptor_type );

    t.register_stdp_connection( t_lastspike_ - get_delay(), get_delay() );
  }
  bool
  send( Event& e, const size_t tid, const new_stp_synapse_nestmlCommonSynapseProperties& cp )
  {
    const double __resolution = nest::Time::get_resolution().get_ms();  // do not remove, this is necessary for the resolution() function

    auto get_thread = [tid]()
    {
        return tid;
    };

    const double __t_spike = e.get_stamp().get_ms();
#ifdef DEBUG
    std::cout << "new_stp_synapse_nestml::send(): handling pre spike at t = " << __t_spike << std::endl;
#endif
    // use accessor functions (inherited from Connection< >) to obtain delay and target
    Node* __target = get_target( tid );
    const double __dendritic_delay = get_delay();
    const bool pre_before_post_update = 0;
    bool pre_before_post_flag = false;

    if (t_lastspike_ < 0.)
    {
        // this is the first presynaptic spike to be processed
        t_lastspike_ = 0.;
    }

    /**
     * update synapse internal state from `t_lastspike_` to `__t_spike`
    **/

    update_internal_state_(t_lastspike_, __t_spike - t_lastspike_, cp);

    const double _tr_t = __t_spike - __dendritic_delay;

    {
        auto get_t = [__t_spike](){ return __t_spike; };    // do not remove, this is in case the predefined time variable ``t`` is used in the NESTML model        
        /**
         *  NESTML generated onReceive code block for presynaptic port "pre_spikes" begins here!
        **/
          double dt = get_t() - S_.t_ls;
          S_.x = 1.0 + (S_.x - 1.0) * std::exp((-dt) / P_.tau_rec);
          S_.u = P_.U + (S_.u - P_.U) * (std::exp((-dt) / P_.tau_fac));
          S_.u = S_.u + P_.U * (1.0 - S_.u);

          /**
           * generated code for emit_spike() function
          **/

          set_delay( get_delay() );
          const long __delay_steps = nest::Time::delay_ms_to_steps( get_delay() );
          set_delay_steps(__delay_steps);
          e.set_receiver( *__target );
          e.set_weight( P_.w * S_.u * S_.x );
          // use accessor functions (inherited from Connection< >) to obtain delay in steps and rport
          e.set_delay_steps( get_delay_steps() );
          e.set_rport( get_rport() );
          e();


          S_.x = S_.x - S_.u * S_.x;
          S_.t_ls = get_t();
    }

    /**
     *  update all convolutions with pre spikes
    **/


    /**
     *  in case pre and post spike time coincide and pre update takes priority
    **/

    if (pre_before_post_flag)
    {
        auto get_t = [__t_spike](){ return __t_spike; };    // do not remove, this is in case the predefined time variable ``t`` is used in the NESTML model      
    }

    /**
     *  synapse internal state has now been fully updated to `__t_spike`
    **/

    t_lastspike_ = __t_spike;
    return true;
  }

  void get_status( DictionaryDatum& d ) const;

  void set_status( const DictionaryDatum& d, ConnectorModel& cm );
};
void
register_new_stp_synapse_nestml( const std::string& name )
{
  nest::register_connection_model< new_stp_synapse_nestml >( name );
}
template < typename targetidentifierT >
constexpr ConnectionModelProperties new_stp_synapse_nestml< targetidentifierT >::properties;


template < typename targetidentifierT >
void
new_stp_synapse_nestml< targetidentifierT >::get_status( DictionaryDatum& __d ) const
{
  ConnectionBase::get_status( __d );
  def< long >( __d, names::size_of, sizeof( *this ) );

  // parameters and state variables  
  def< double >( __d, names::weight, P_.w );    // NEST special case for weight variable
  def< double >( __d, nest::new_stp_synapse_nestml_names::_w, P_.w );    // NEST special case for weight variable
  def< double >(__d, nest::new_stp_synapse_nestml_names::_U, get_U());
  def< double >(__d, nest::new_stp_synapse_nestml_names::_tau_rec, get_tau_rec());
  def< double >(__d, nest::new_stp_synapse_nestml_names::_tau_fac, get_tau_fac());
  def< double >( __d, names::delay, get_delay() );    // NEST special case for delay variable
  def<double>(__d, nest::new_stp_synapse_nestml_names::_delay, get_delay());
  def< double >(__d, nest::new_stp_synapse_nestml_names::_u, get_u());
  def< double >(__d, nest::new_stp_synapse_nestml_names::_x, get_x());
  def< double >(__d, nest::new_stp_synapse_nestml_names::_t_ls, get_t_ls());
}

template < typename targetidentifierT >
void
new_stp_synapse_nestml< targetidentifierT >::set_status( const DictionaryDatum& __d,
  ConnectorModel& cm )
{
  if (__d->known(nest::new_stp_synapse_nestml_names::_w) and __d->known(nest::names::weight))
  {
    throw BadProperty( "To prevent inconsistencies, please set either 'weight' or 'w' variable; not both at the same time." );
  }

  // call parent class method
  ConnectionBase::set_status( __d, cm );

  // state variables and parameters  
  double tmp_u = get_u();
  updateValue<double>(__d, nest::new_stp_synapse_nestml_names::_u, tmp_u);
  double tmp_x = get_x();
  updateValue<double>(__d, nest::new_stp_synapse_nestml_names::_x, tmp_x);
  double tmp_t_ls = get_t_ls();
  updateValue<double>(__d, nest::new_stp_synapse_nestml_names::_t_ls, tmp_t_ls);
  // special treatment of NEST weight
  double tmp_w = get_weight();
  if (__d->known(nest::new_stp_synapse_nestml_names::_w))
  {
    updateValue<double>(__d, nest::new_stp_synapse_nestml_names::_w, tmp_w);
  }
  if (__d->known(nest::names::weight))
  {
    updateValue<double>(__d, nest::names::weight, tmp_w);
  }
  double tmp_U = get_U();
  updateValue<double>(__d, nest::new_stp_synapse_nestml_names::_U, tmp_U);
  double tmp_tau_rec = get_tau_rec();
  updateValue<double>(__d, nest::new_stp_synapse_nestml_names::_tau_rec, tmp_tau_rec);
  double tmp_tau_fac = get_tau_fac();
  updateValue<double>(__d, nest::new_stp_synapse_nestml_names::_tau_fac, tmp_tau_fac);
  // special treatment of NEST delay
  double tmp_delay = get_delay();
  updateValue<double>(__d, nest::new_stp_synapse_nestml_names::_delay, tmp_delay);

  // We now know that (ptmp, stmp) are consistent. We do not
  // write them back to (P_, S_) before we are also sure that
  // the properties to be set in the parent class are internally
  // consistent.
  ConnectionBase::set_status( __d, cm );

  // if we get here, temporaries contain consistent set of properties

  // set state and parameters  
  set_u(tmp_u);
  set_x(tmp_x);
  set_t_ls(tmp_t_ls);
  set_w(tmp_w);
  set_U(tmp_U);
  set_tau_rec(tmp_tau_rec);
  set_tau_fac(tmp_tau_fac);
  // special treatment of NEST delay
  set_delay(tmp_delay);



  // recompute internal variables in case they are dependent on parameters or state that might have been updated in this call to set_status()
  V_.__h = nest::Time::get_resolution().get_ms();
  recompute_internal_variables();
}

/**
 * NESTML internals block symbols initialisation
**/
template < typename targetidentifierT >
void new_stp_synapse_nestml< targetidentifierT >::recompute_internal_variables()
{
  const double __resolution = nest::Time::get_resolution().get_ms();  // do not remove, this is necessary for the resolution() function


}

/**
 * constructor
**/
template < typename targetidentifierT >
new_stp_synapse_nestml< targetidentifierT >::new_stp_synapse_nestml() : ConnectionBase()
{
  const double __resolution = nest::Time::get_resolution().get_ms();  // do not remove, this is necessary for the resolution() function

  // initial values for parameters  
  P_.w = 1.0; // as real
  P_.U = 0.19; // as real
  P_.tau_rec = 200.0; // as ms
  P_.tau_fac = 1500.0; // as ms

  V_.__h = nest::Time::get_resolution().get_ms();
  recompute_internal_variables();

  // initial values for state variables  
  S_.u = 0.19; // as real
  S_.x = 1.0; // as real
  S_.t_ls = 0.0; // as ms

  t_lastspike_ = 0.;
}

/**
 * copy constructor
**/
template < typename targetidentifierT >
new_stp_synapse_nestml< targetidentifierT >::new_stp_synapse_nestml( const new_stp_synapse_nestml< targetidentifierT >& rhs )
: ConnectionBase( rhs )
{
  // parameters
  P_.U = rhs.P_.U;
  P_.tau_rec = rhs.P_.tau_rec;
  P_.tau_fac = rhs.P_.tau_fac;

  // state variables
  S_.u = rhs.S_.u;
  S_.x = rhs.S_.x;
  S_.t_ls = rhs.S_.t_ls;
  t_lastspike_ = rhs.t_lastspike_;

  // special treatment of NEST delay
  set_delay(rhs.get_delay());
  // special treatment of NEST weight
  set_weight(rhs.get_weight());
}

template < typename targetidentifierT >
inline void
new_stp_synapse_nestml< targetidentifierT >::update_internal_state_(double t_start, double timestep, const new_stp_synapse_nestmlCommonSynapseProperties& cp)
{
    if (timestep < 1E-12)
    {
#ifdef DEBUG
        std::cout << "\tupdate_internal_state_() called with dt < 1E-12; skipping update\n" ;
#endif
        return;
    }

    const double __resolution = timestep;  // do not remove, this is necessary for the resolution() function
    auto get_t = [t_start](){ return t_start; };   // do not remove, this is in case the predefined time variable ``t`` is used in the NESTML model

#ifdef DEBUG
    std::cout<< "\tUpdating internal state: t_start = " << t_start << ", dt = " << timestep << "\n";
#endif

    V_.__h = timestep;
    assert(V_.__h > 0);
    recompute_internal_variables();

    /**
     * Begin NESTML generated code for the update block
    **/

    /**
     * End NESTML generated code for the update block
    **/
}

} // namespace

#endif /* #ifndef NEW_STP_SYNAPSE_NESTML_H */