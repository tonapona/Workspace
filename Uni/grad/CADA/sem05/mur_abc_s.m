%Code mur_abc.m
%This software simulates reflection at the boundary terminated with first-order Mur ABC. 
%The programme should be run for sufficient number of time steps
%so that the excitation exits the space domain and the reflection from the
%right mur boundary enters the space domain. Modulated gaussian pulse is used for %excitation with centre frequency at 1 GHz. The first plot gives the reflected waveform.
%The second plot gives the time waveform about the node is.


clc
clear
close all
clf
data=[];

alpha = 0.9;
mu0=4*pi*1e-7;   
e0=8.854e-12;
c=1/sqrt(mu0*e0);
dx = 4.2e-2;
dt=alpha*dx/c;
is = 350;   % node at which the incident and reflected waves are sampled to determine the reflection
fc = 1e9;  % modulating frequency
lambda = c/fc;
xend = 400; % number of nodes
t0 = 3e-09;	% peak position of Gaussian pulse in time
dxl = dx/lambda;
spc_indx=0:xend;
den = asin(sin(pi*alpha*dxl)/alpha);
vph_c = pi*dxl/den;  % normalized phase velocity
t_is = t0/dt+xend/vph_c/alpha+(xend-is)/vph_c/alpha;   % time taken by the peak of reflected % wave to travel back to node is 
tend = round(t_is*1.2); % The factor 1.2 is arbitrary. It helps capture the reflected wave fully.

e=zeros(length(spc_indx),1); h=e; 
ep=e; hp=h;                     % initialize previous values of e & h

hndl=plot(e);                   % get the handle to the plot
set(hndl,'EraseMode','xor') 	% for simulation of wave propagation
for n = 1:tend
	for i=1:400                 % simulate for h-nodes
        h(i)=(ep(i)-ep(i+1))*dt/dx/mu0+hp(i); 		% curl e = -del b/ del t;
    end
	h(i+1)=hp(i)+(alpha-1)/(alpha+1)*(h(i)-hp(i+1)); % ABC for right boundary
    
    for i=2:400                 % simulate for e-nodes
        e(i)=(h(i-1)-h(i))*dt/dx/e0 +ep(i);  % curl b = mu*epsilon*del e/ del t;
    end
   
	e(i+1)=ep(i)+(alpha-1)/(alpha+1)*(e(i)-ep(i+1)); % ABC for right boundary
	e(1)=ep(2)+(alpha-1)/(alpha+1)*(e(2)-ep(1)); % ABC for left boundary
    
 %%%%%%%%%%%%%%%%%% launch a modulated Gaussian pulse
   T = t0/3;		% specify pulse width
   y(n) = exp(-(((n-1)*dt-t0)/T).^2)*cos(2*pi*fc*((n-1)*dt-t0)); % modulated Gaussian pulse
   if n*dt <= 2*t0*1.1  % The factor 1.1 is arbitrary.
        e(1)= y(n); 
   else
       e(1)=0;
   end
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    hp=h;ep=e;         % store the previous values in appropriate vectors
    drawnow;           % refresh data and plot the current condition of the pulse
    set(hndl,'YData',(e));
    data=[data e(is)]; 	% time waveform at node is 
end
figure
plot(data);
title ('Time waveform at node is');
xlabel('time step n');
ylabel('amplitude');

% partitioning of time waveform at node is into incident and
% reflected fields to determine the reflection coefficient
tpeak = round(t0/dt + is/vph_c/alpha);  %peaking instant for the incident wave at node is

%n1 marks the end of incident wave. Its value may be selected suitably for
%large dx values.
n1 = round(tpeak+t0/dt);
datai = data(1:n1);    		% incident waveform about node is 
datar = data(n1:tend); 		% reflected waveform about node is 
peak_inc = max(abs(datai)); % peak value of incident waveform
peak_ref = max(abs(datar)); % peak value of reflected waveform
ref = peak_ref/peak_inc 	% reflection coefficient due to ABC at right

