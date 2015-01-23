#include <ost/mol/mm/state_extractor.hh>


namespace ost { namespace mol{ namespace mm{

void StateExtractor::ExtractPotentialEnergy(boost::shared_ptr<OpenMM::Context> context,
  	                                        Real& energy){

  OpenMM::State s = context->getState(OpenMM::State::Energy);
  energy = s.getPotentialEnergy();
}

void StateExtractor::ExtractKineticEnergy(boost::shared_ptr<OpenMM::Context> context,
	                                        Real& energy){

  OpenMM::State s = context->getState(OpenMM::State::Energy);
  energy = s.getKineticEnergy();
}

void StateExtractor::ExtractEnergy(boost::shared_ptr<OpenMM::Context> context,
	                                 Real& energy){

  OpenMM::State s = context->getState(OpenMM::State::Energy);
  energy = s.getKineticEnergy() + s.getPotentialEnergy();
}

void StateExtractor::ExtractPositions(boost::shared_ptr<OpenMM::Context> context,
	                                    geom::Vec3List& positions, bool enforce_periodic_box, 
                                      bool in_angstrom){

  positions.resize(context->getSystem().getNumParticles());
  OpenMM::State s = context->getState(OpenMM::State::Positions, enforce_periodic_box);
  const std::vector<OpenMM::Vec3>& p = s.getPositions();
  int actual_index = 0;
  for(std::vector<OpenMM::Vec3>::const_iterator i = p.begin(); i != p.end(); ++i){
    positions[actual_index] = geom::Vec3((*i)[0],(*i)[1],(*i)[2]);
    ++actual_index;
  }
  if(in_angstrom) positions*=10.0;
}

void StateExtractor::ExtractVelocities(boost::shared_ptr<OpenMM::Context> context,
	                                     geom::Vec3List& velocities){

  velocities.resize(context->getSystem().getNumParticles());
  OpenMM::State s = context->getState(OpenMM::State::Velocities);
  const std::vector<OpenMM::Vec3>& v = s.getVelocities();
  int actual_index = 0;
  for(std::vector<OpenMM::Vec3>::const_iterator i = v.begin(); i != v.end(); ++i){
    velocities[actual_index] = geom::Vec3((*i)[0],(*i)[1],(*i)[2]);
    ++actual_index;
  }
}

void StateExtractor::ExtractForces(boost::shared_ptr<OpenMM::Context> context,
	                                 geom::Vec3List& forces){

  forces.resize(context->getSystem().getNumParticles());
  OpenMM::State s = context->getState(OpenMM::State::Forces);
  const std::vector<OpenMM::Vec3>& f = s.getForces();
  int actual_index = 0;
  for(std::vector<OpenMM::Vec3>::const_iterator i = f.begin(); i != f.end(); ++i){
    forces[actual_index] = geom::Vec3((*i)[0],(*i)[1],(*i)[2]);
    ++actual_index;
  }
}


}}} //ns
