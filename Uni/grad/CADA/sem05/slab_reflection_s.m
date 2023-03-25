% Code slab_reflection.m		Courtesy: Debesh Bhatta
% Gaussian pulse propagation and reflection from a slab 

clc;
clear;
close all;
clf

%specify the number of time steps over which the simulations are to be performed
tend = 1000;
alpha = 0.5;   		 %specify the value of alpha
mu0=4*pi*1e-7;   e0=8.854e-12;
c=1/sqrt(mu0*e0);

dx=1.5e-3;          %space step
dt = alpha*dx/c;	%time step

spc_indx=[0:tend*alpha+1];	
e=zeros(length(spc_indx),1); h=e; 
ep=e; hp=h;                     %initialize previous values of e & h

hndl=plot(e);                   % get the handle to the plot
set(hndl,'EraseMode','xor') 	% for simulation of wave propagation

for n = 1:tend
	for i=1:350                 % simulate for h-nodes
        if (i >= 100 && i <= 200) || (i >= 250 && i <= 350)
           mur=1; er=4;
        else
            mur=1; er=1; 
        end
        mu=mu0*mur; epsilon=e0*er;
        h(i)=(ep(i)-ep(i+1))*(dt/dx)/mu +hp(i); 	% curl e = -del b/ del t;
    end

    alpha=(c/sqrt(mur*er))*dt/dx;                      %alpha for loaded layers
	h(i+1)=hp(i)+((alpha-1)/(alpha+1))*(h(i)-hp(i+1)); 	%ABC for right boundary
    alpha=c*dt/dx;
    
    for i=1:350    				% simulate for e-nodes
        if (i >= 100 && i <= 200) || (i >= 250 && i <= 350)
           mur=1; er=4;
        else
            mur=1; er=1; 
        end
        mu=mu0*mur; epsilon=e0*er;
        e(i)=(h(i-1)-h(i))*(dt/dx)/epsilon +ep(i);  % curl b = mu*epsilon*del e/ del t;
    
    end
    alpha=(c/sqrt(mur*er))*dt/dx;                      %alpha for dielectric layers
    e(i+1)=ep(i)+((alpha-1)/(alpha+1))*(e(i)-ep(i+1)); % ABC for right boundary
    alpha=c*dt/dx;
    er=1; mur=1;                                      %alpha for free space layers
    alpha=(c/sqrt(mur*er))*dt/dx;    
	e(1)=ep(2)+((alpha-1)/(alpha+1))*(e(2)-ep(1)); % ABC for left boundary
        
    %%%%%%%%%%%%%Gaussian pulse excitation of the grid
    pwidth=400e-12;
    if n*dt <= pwidth*1.1  
        e(1)= exp(-((n*dt-pwidth/2)/(pwidth/6))^2); 	%Gaussian pulse
    else
        e(1)=0;
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    hp=h;ep=e;  		%store the previous values in appropriate vectors
    drawnow;           %refresh data and plot the current condition of the wave pulse
    set(hndl,'YData',(e));
    title('Plot of reflected and transmitted waves, \epsilon_r = 4');
    ylim([-1 1])	
    xlabel('node number');
    ylabel('amplitude');

   % specify the time instant at which the propagating pulse is displayed
%      if n==700 
%          figure; plot(e); 
%      end
end
